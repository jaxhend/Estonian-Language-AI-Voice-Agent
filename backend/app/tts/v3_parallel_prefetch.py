# app/tts/v3_parallel_prefetch.py
import asyncio
import contextlib
import aiohttp
import io
import re
from typing import List, Tuple, Dict

from app.bus import bus
from app.schemas.events import ManagerAnswer, TTSAudio

# --- Lausepõhine tükeldus + lihtne prosoodia ---
_SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def split_sentences(text: str, max_chars: int = 220) -> List[str]:
    """Lausepõhine tükeldus; väga pikad lõigud lõigatakse tühiku lähedalt."""
    raw = _SENT_SPLIT.split((text or "").strip())
    parts: List[str] = []
    for s in raw:
        s = s.strip()
        if not s:
            continue
        if len(s) <= max_chars:
            parts.append(s)
        else:
            buf = []
            for w in s.split():
                buf.append(w)
                if sum(len(x) + 1 for x in buf) > max_chars:
                    parts.append(" ".join(buf))
                    buf = []
            if buf:
                parts.append(" ".join(buf))
    return parts

def prosody_prep(s: str) -> str:
    """Lihtsad eestipärased parandused: komad, ühikud, %-d, kellaajad."""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(?<=\d)\.(?=\d)", ",", s)           # 3.5 -> 3,5
    s = re.sub(r"(\d+)\s*%", r"\1 protsenti", s)     # 25% -> 25 protsenti
    s = re.sub(r"(\d+)\s*€", r"\1 eurot", s)         # 15€ -> 15 eurot
    s = re.sub(r"€\s*(\d+)", r"\1 eurot", s)         # €15 -> 15 eurot
    s = re.sub(r"(\d+)\s*km\b", r"\1 kilomeetrit", s, flags=re.I)
    s = re.sub(r"(\d+)\s*kg\b", r"\1 kilogrammi", s, flags=re.I)
    s = re.sub(r"(\d+)\s*cm\b", r"\1 sentimeetrit", s, flags=re.I)
    s = re.sub(r"(\d+)\s*mm\b", r"\1 millimeetrit", s, flags=re.I)
    s = re.sub(r"(\d+)\s*m\b",  r"\1 meetrit",     s, flags=re.I)
    s = re.sub(r"(\d+)\s*h\b",  r"\1 tundi",       s, flags=re.I)
    # pehmed pausid (valikuline): em-kriips “ – ” hoiab mõttepausi
    return s

class V3ParallelPrefetchTTS:
    """
    ElevenLabs v3 HTTP 'prefetch':
    - teeb mitu päringut paralleelselt (ühise ClientSessioniga),
    - hakkab esitama NII PEA kui järgmine järjekorras olev lause on valmis,
    - hoiab lausepiirid (loomulik kõla).
    """
    def __init__(
        self,
        api_key: str,
        voice_id: str,
        language_code: str = "et",
        model_id: str = "eleven_v3",
        max_concurrency: int = 3,     # tõsta/langeta vastavalt limiitidele
        chunk_emit_size: int = 2048,  # väiksem → tihedam push → kiirem algus
        stability: float = 0.5,       # v3: 0.0 | 0.5 | 1.0
        output_format: str = "mp3_44100_64",  # balanced speed/quality for v3
    ):
        self.api_key = api_key
        self.voice_id = voice_id
        self.language_code = language_code
        self.model_id = model_id
        self.max_concurrency = max_concurrency
        self.chunk_emit_size = chunk_emit_size
        self.stability = stability
        self.output_format = output_format

    async def _fetch_one(self, session: aiohttp.ClientSession, idx: int, text: str) -> Tuple[int, bytes]:
        """Tõmbab ühe lause MP3-ks ja tagastab (index, mp3_bytes)."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        if self.output_format:
            url += f"?output_format={self.output_format}"

        headers = {
            "xi-api-key": self.api_key,
            "Accept": "application/octet-stream",
            "User-Agent": "voice-agent/0.1",
        }
        body = {
            "text": prosody_prep(text),
            "model_id": self.model_id,
            "language_code": self.language_code,
            "voice_settings": {"stability": self.stability},  # v3 diskreetsed väärtused
        }

        buff = io.BytesIO()
        async with session.post(url, headers=headers, json=body) as resp:
            if resp.status == 403:
                detail = await resp.text()
                raise RuntimeError(f"403 (gated): {detail}")
            resp.raise_for_status()
            async for chunk in resp.content.iter_chunked(8192):  # võid ka 4096 võtta
                if chunk:
                    buff.write(chunk)
        return idx, buff.getvalue()

    async def stream(self, event: ManagerAnswer):
        """
        1) Tükelda tekst lauseteks.
        2) Käivita paralleelsed päringud (semafor), ÜHE ClientSessioniga.
        3) Esita järjest kohe, kui järgmine indeks on valmis (ei oota kõiki).
        """
        from app.api.ws import active_connections

        parts = split_sentences(event.text)
        if not parts:
            if event.client_id in active_connections:
                await active_connections[event.client_id].send_json({"isFinal": True})
            return

        timeout = aiohttp.ClientTimeout(total=120, connect=8, sock_read=90)
        sem = asyncio.Semaphore(self.max_concurrency)

        results: Dict[int, bytes] = {}
        ready_events = [asyncio.Event() for _ in range(len(parts))]
        next_to_emit = 0

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async def worker(i: int, t: str):
                nonlocal results
                async with sem:
                    idx, mp3 = await self._fetch_one(session, i, t)
                    results[idx] = mp3
                    ready_events[idx].set()

            tasks = [asyncio.create_task(worker(i, t)) for i, t in enumerate(parts)]

            # Emitteri tsükkel: oota alati JÄRGMIST indeksit ja esita kohe
            try:
                while next_to_emit < len(parts):
                    await ready_events[next_to_emit].wait()  # oota kuni just see lause on valmis
                    mp3 = results.pop(next_to_emit)
                    # tükelda väikesteks pakkideks ja saada kliendile
                    mv = memoryview(mp3)
                    pos = 0
                    step = self.chunk_emit_size
                    while pos < len(mv):
                        chunk = mv[pos:pos+step].tobytes()
                        pos += step
                        await bus.publish("tts.audio", TTSAudio(chunk=chunk, client_id=event.client_id))
                    next_to_emit += 1
            except Exception as e:
                print(f"[v3-prefetch] emit error: {e}")
            finally:
                # lõpeta tööd kenasti
                for t in tasks:
                    with contextlib.suppress(asyncio.CancelledError):
                        if not t.done():
                            t.cancel()
                for t in tasks:
                    with contextlib.suppress(asyncio.CancelledError, Exception):
                        await t

        # Lõpu-signal
        try:
            if event.client_id in active_connections:
                await active_connections[event.client_id].send_json({"isFinal": True})
        except Exception as se:
            print(f"[v3-prefetch] could not send isFinal: {se}")