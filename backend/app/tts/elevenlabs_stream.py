from app.bus import bus
from app.core.config import ELEVENLABS_API_KEY
from app.schemas.events import ManagerAnswer
from app.tts.v3_parallel_prefetch import V3ParallelPrefetchTTS
from app.tts.elevenlabs_http_stream import ElevenLabsHTTPStream  # for short messages

VOICE_ID = "tIFPE2y0DAU6xfZn3Fka"  # ← replace with your own working Estonian-capable voice
LANGUAGE_CODE = "et"


def _is_short(text: str) -> bool:
    """Heuristic: short text → faster single HTTP stream."""
    if not text:
        return True
    sentences = len([s for s in text.replace("\n", " ").split(".") if s.strip()])
    return len(text) <= 240 or sentences <= 2


@bus.subscribe("manager.answer")
async def on_manager_answer(event: ManagerAnswer):
    if not ELEVENLABS_API_KEY:
        print("ELEVENLABS_API_KEY missing; TTS disabled.")
        return

    # Choose fast path (single stream) vs parallel prefetch
    if _is_short(event.text):
        # --- Short text path (direct /stream for minimal latency)
        tts = ElevenLabsHTTPStream(
            api_key=ELEVENLABS_API_KEY,
            voice_id=VOICE_ID,
            model_id="eleven_v3",
            language_code=LANGUAGE_CODE,
        )
        await tts.stream(event)
        return

    # --- Long text path (parallel prefetch by sentence)
    tts = V3ParallelPrefetchTTS(
        api_key=ELEVENLABS_API_KEY,
        voice_id=VOICE_ID,
        language_code=LANGUAGE_CODE,
        model_id="eleven_v3",
        max_concurrency=3,     # tweak if needed
        chunk_emit_size=8192,  # outgoing chunks to WS
        stability=0.5,         # allowed: 0.0 | 0.5 | 1.0
        output_format="mp3_44100_64",  # balanced speed/quality
    )
    await tts.stream(event)