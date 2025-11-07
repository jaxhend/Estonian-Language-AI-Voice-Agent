# app/tts/elevenlabs_http_stream.py
import aiohttp
from app.bus import bus
from app.schemas.events import ManagerAnswer, TTSAudio

class ElevenLabsHTTPStream:
    """
    Simple HTTP TTS streamer for ElevenLabs v3.
    Streams audio bytes directly to the frontend over the event bus.
    No chunking or pipelining.
    """

    def __init__(self, api_key: str, voice_id: str, model_id: str = "eleven_v3", language_code: str = "et"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.language_code = language_code

    async def stream(self, event: ManagerAnswer):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "application/octet-stream",
            "User-Agent": "voice-agent/0.1"
        }

        # ✅ v3 only allows stability: 0.0, 0.5, or 1.0
        body = {
            "text": event.text,
            "model_id": self.model_id,  # "eleven_v3"
            "voice_settings": {"stability": 0.5},  # Natural
            "language_code": self.language_code   # Estonian
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if resp.status == 403:
                    txt = await resp.text()
                    print(f"[elevenlabs/http] 403 Forbidden for model {self.model_id}: {txt}")
                    return
                elif resp.status != 200:
                    txt = await resp.text()
                    print(f"[elevenlabs/http] {resp.status}: {txt}")
                    return

                # Stream binary MP3 chunks as they arrive
                async for chunk in resp.content.iter_chunked(8192):
                    if chunk:
                        await bus.publish("tts.audio", TTSAudio(chunk=chunk, client_id=event.client_id))

        # Signal end-of-stream to the WebSocket client
        from app.api.ws import active_connections
        if event.client_id in active_connections:
            await active_connections[event.client_id].send_json({"isFinal": True})