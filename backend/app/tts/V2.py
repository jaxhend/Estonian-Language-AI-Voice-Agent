import os
import sys
import requests
import pyaudio
import shutil
import subprocess
from dotenv import load_dotenv
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.context_loader import format_context_for_llm
from app.services.conversation_history import format_history_for_llm, add_message_to_history
from app.services.booking_manager import create_booking

# --- Load environment ---
load_dotenv()

# -------------------- GOOGLE STT CONFIG --------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
RECOGNIZER_NAME = os.getenv("RECOGNIZER_NAME")
RECOGNIZER = f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/{RECOGNIZER_NAME}"

MIC_RATE = 8000
MIC_CHUNK = 100  # frames per read

# -------------------- LLM CONFIG --------------------
LLM_URL        = os.getenv("LLM_URL", "http://31.22.104.92:8000/v1/completions")
LLM_MODEL      = os.getenv("LLM_MODEL", "google/gemma-3-27b-it")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "250"))
LLM_TIMEOUT_S  = float(os.getenv("LLM_TIMEOUT_S", "30"))

# -------------------- BUSINESS CONTEXT --------------------
BUSINESS_CONTEXT = format_context_for_llm()
CLIENT_ID = uuid4()  # Unique session ID

print(f"📋 Session ID: {CLIENT_ID}")
print("📚 Business context loaded\n")

# -------------------- ELEVENLABS v3 TTS CONFIG --------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID           = os.getenv("ELEVENLABS_VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"
LANGUAGE_CODE      = os.getenv("ELEVENLABS_LANG", "et")
TTS_OUTPUT_FORMAT  = "mp3_44100_64"  # Works on all plans; high-quality MP3 stream

# -------------------- MICROPHONE STREAM --------------------
def mic_stream():
    """Generator yielding small mic chunks for streaming_recognize()."""
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=MIC_RATE,
        input=True,
        frames_per_buffer=MIC_CHUNK,
    )
    print("🎙️ Mic active. Speak now (Ctrl+C to stop)...\n")
    try:
        while True:
            data = stream.read(MIC_CHUNK, exception_on_overflow=False)
            yield cloud_speech.StreamingRecognizeRequest(audio=data)
    except GeneratorExit:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

# -------------------- LLM CALL --------------------
def call_llm(user_text: str) -> str:
    """Send the recognized text to the LLM with business context and conversation history."""

    # Get conversation history
    conversation_history = format_history_for_llm(CLIENT_ID, limit=5)

    # Build comprehensive prompt
    system_prompt = f"""Sa oled abivalmis eestikeelne AI assistent broneerimissüsteemi jaoks.

OLULINE KONTEKST SINU ETTEVÕTTE KOHTA:
{BUSINESS_CONTEXT}

BRONEERIMISE PROTSESS:
1. Küsi kasutajalt, millist teenust ta soovib
2. Küsi soovitud aega ja kuupäeva
3. Küsi soovitud asukohta
4. Küsi kliendi nimi ja kontakttelefon
5. Kinnita kõik detailid kasutajale
6. Kui kasutaja kinnitab, kasuta BOOKING_CONFIRMED märgendit

OLULINE: Kui kasutaja kinnitab broneeringu (ütleb "jah", "kinnitan", "broneeri", vms), 
lisa oma vastuse LÕPPU täpselt see märgend formaadis:
BOOKING_CONFIRMED|teenus_id|teenus_nimi|kuupäev_ja_kellaaeg|asukoht_id|asukoht_nimi|kliendi_nimi|telefon|märkused

JUHISED:
- Ole sõbralik, professionaalne ja lühike
- Vasta eesti keeles
"""

    full_prompt = system_prompt + "\n\n"

    if conversation_history:
        full_prompt += f"{conversation_history}\n"

    full_prompt += f"Kasutaja: {user_text}\n\nAssistent:"

    payload = {"model": LLM_MODEL, "prompt": full_prompt, "max_tokens": LLM_MAX_TOKENS}
    r = requests.post(LLM_URL, json=payload, timeout=LLM_TIMEOUT_S)
    r.raise_for_status()
    js = r.json()
    answer = (js.get("choices") or [{}])[0].get("text", "").strip()

    # Check if response contains booking confirmation marker
    if "BOOKING_CONFIRMED|" in answer:
        parts = answer.split("BOOKING_CONFIRMED|")
        if len(parts) > 1:
            booking_data = parts[1].split("|")
            if len(booking_data) >= 7:
                service_id, service_name, date_time, location_id, location_name, customer_name, customer_phone = booking_data[:7]
                notes = booking_data[8] if len(booking_data) > 8 else ""

                # Create the booking
                booking_id = create_booking(
                    client_id=CLIENT_ID,
                    service_id=service_id.strip(),
                    service_name=service_name.strip(),
                    date_time=date_time.strip(),
                    location_id=location_id.strip(),
                    location_name=location_name.strip(),
                    customer_name=customer_name.strip(),
                    customer_phone=customer_phone.strip(),
                    notes=notes.strip() if notes else None
                )

                if booking_id:
                    print(f"\n📅 Booking created: {booking_id[:8]}...")
                    # Remove the marker from response
                    answer = parts[0].strip()
                    answer += f"\n\nTeie broneering on salvestatud ja ootab kinnitust. Broneeringu number: {booking_id[:8]}"

    # Save conversation to history
    add_message_to_history(CLIENT_ID, user_text, answer)

    return answer

# -------------------- ELEVENLABS STREAMED MP3 TTS --------------------
def speak_elevenlabs_v3_stream(text: str):
    """
    Stream ElevenLabs v3 MP3 directly into mpg123 for smooth, low-latency playback.
    Handles long clips without timing out.
    """
    import time

    if not ELEVENLABS_API_KEY:
        print("⚠️ ELEVENLABS_API_KEY missing; skipping TTS.")
        return
    if not shutil.which("mpg123"):
        print("⚠️ 'mpg123' not found. Install with: brew install mpg123")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream?output_format={TTS_OUTPUT_FORMAT}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Accept": "application/octet-stream",
        "User-Agent": "voice-agent/0.1",
    }
    body = {
        "text": text,
        "model_id": "eleven_v3",
        "language_code": LANGUAGE_CODE,
        "voice_settings": {"stability": 0.5},  # valid: 0.0, 0.5, or 1.0
    }

    # Create mpg123 subprocess
    mpg_args = ["mpg123", "-q", "--buffer", "2048", "--preload", "0", "-"]
    proc = subprocess.Popen(
        mpg_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        with requests.post(url, headers=headers, json=body, stream=True, timeout=(6, 90)) as resp:
            if resp.status_code in (400, 403):
                print(f"[TTS] HTTP {resp.status_code}: {resp.text}")
                return
            resp.raise_for_status()

            # Stream MP3 chunks directly to mpg123
            for chunk in resp.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                try:
                    proc.stdin.write(chunk)
                    proc.stdin.flush()
                except BrokenPipeError:
                    # Player finished early (EOF)
                    return
    finally:
        # Close stdin so mpg123 drains and finishes playing
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass

        # Wait gracefully (up to 15 seconds for long speech)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()

# -------------------- MAIN EVENT LOOP --------------------
def main():
    client = speech_v2.SpeechClient(client_options={"api_endpoint": f"{LOCATION}-speech.googleapis.com"})

    explicit = cloud_speech.ExplicitDecodingConfig(
        encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=MIC_RATE,
        audio_channel_count=1,
    )

    cfg = cloud_speech.RecognitionConfig(
        explicit_decoding_config=explicit,
        language_codes=["et-EE"],
        model="chirp_3",
    )

    stream_cfg = cloud_speech.StreamingRecognitionConfig(config=cfg)
    config_req = cloud_speech.StreamingRecognizeRequest(recognizer=RECOGNIZER, streaming_config=stream_cfg)

    def reqs():
        yield config_req
        yield from mic_stream()

    responses = client.streaming_recognize(requests=reqs())

    try:
        for response in responses:
            if not response.results:
                continue
            for result in response.results:
                transcript = result.alternatives[0].transcript.strip()
                if not transcript:
                    continue

                if result.is_final:
                    print(f"\n✅ Final: {transcript}")

                    try:
                        answer = call_llm(transcript)
                        print(f"🤖 LLM: {answer}")
                        speak_elevenlabs_v3_stream(answer)
                    except Exception as e:
                        print(f"LLM/TTS error: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"🕓 Interim: {transcript}", end="\r", flush=True)
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

# -------------------- RUN --------------------
if __name__ == "__main__":
    main()