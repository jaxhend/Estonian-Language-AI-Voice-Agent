import asyncio
import os
import traceback

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# --- Configuration Constants ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000  # 16kHz is required for Gemini Live
CHUNK_SIZE = 1024

MODEL = "gemini-live-2.5-flash-preview"

# --- Gemini Client Setup ---
# ⚠️ Ensure GEMINI_API_KEY is set in your environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=API_KEY
)

# Configuration for LiveConnect session
# Requesting only "TEXT" response modality
CONFIG = types.LiveConnectConfig(
    response_modalities=["TEXT"],
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    # Note: Compression is optional but included here
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
    system_instruction=(
        "VÄLJASTA KASUTAJA SISEND SÕNA-SÕNALT."
        "PROOVI PARANDADA LAUSED TÄIELIKUKS"
    )
    # IMPORTANT: No voice_config is present, as we only want text output.
)

pya = pyaudio.PyAudio()


class AudioToText:
    def __init__(self):
        self.session = None
        self.out_queue = None
        self.audio_stream = None

    async def listen_audio(self):
        """Capture microphone audio chunks and put them in the queue."""
        try:
            mic_info = pya.get_default_input_device_info()
            self.audio_stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=SEND_SAMPLE_RATE,
                input=True,
                input_device_index=mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )

            print("Starting microphone stream...")
            while True:
                # Read audio data from the microphone (blocking call, use to_thread)
                data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False)

                # ✅ FIX: Use the complete MIME type for raw 16kHz PCM audio
                await self.out_queue.put({"data": data, "mime_type": "audio/pcm;rate=16000"})
        except Exception:
            traceback.print_exc()

    async def send_audio(self):
        """Send microphone audio chunks to Gemini's LiveConnect session."""
        try:
            while True:
                chunk = await self.out_queue.get()
                await self.session.send(input=chunk)
        except Exception:
            traceback.print_exc()

    async def receive_text(self):
        """Receive live transcription text from Gemini."""
        try:
            while True:
                # session.receive() yields an async iterable of turns
                turn = self.session.receive()

                # Iterate over responses within the current turn
                async for response in turn:
                    # Check for the transcribed text
                    if response.text:
                        print(f"🗣️ {response.text.strip()}")
        except Exception:
            traceback.print_exc()

    async def run(self):
        """Main method to initialize the session and tasks."""
        try:
            # Use async context manager for the LiveConnect session and TaskGroup
            async with (
                client.aio.live.connect(model=MODEL,
                                        config=CONFIG, ) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.out_queue = asyncio.Queue(maxsize=10)  # Bounded queue for audio chunks

                # Start the three main concurrent tasks
                tg.create_task(self.listen_audio())
                tg.create_task(self.send_audio())
                tg.create_task(self.receive_text())

                print("🎤 Speak into your microphone — press Ctrl+C to stop.")
                await asyncio.Future()  # Run the task group forever

        except asyncio.CancelledError:
            print("\nShutting down...")
            pass
        except Exception as e:
            traceback.print_exc()
        finally:
            if self.audio_stream:
                print("Closing audio stream.")
                self.audio_stream.close()


if __name__ == "__main__":
    try:
        asyncio.run(AudioToText().run())
    except KeyboardInterrupt:
        print("Program stopped by user.")
    finally:
        pya.terminate()
