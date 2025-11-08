import asyncio
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech

from app.bus import bus
from app.schemas.events import ClientAudio, STTFinal, STTPartial

load_dotenv()



class GoogleSTT:

    def __init__(self, client_id, recognizer_path: str | None = None, language: str = "et-EE"):
        load_dotenv()

        # Configuration
        GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        print(GOOGLE_APPLICATION_CREDENTIALS)
        self.PROJECT_ID = os.getenv("PROJECT_ID")
        self.LOCATION = os.getenv("LOCATION")
        self.RECOGNIZER_NAME = os.getenv("RECOGNIZER_NAME")

        if GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

        self.RECOGNIZER = f"projects/{self.PROJECT_ID}/locations/{self.LOCATION}/recognizers/{self.RECOGNIZER_NAME}"
        self.RATE = 16000  # Sample rate needs to match frontend
        self.CHUNK = 1024 * 4

        self.client_id = client_id
        self._client = speech_v2.SpeechAsyncClient(
            client_options={"api_endpoint": f"{self.LOCATION}-speech.googleapis.com"}
        )
        self._audio_queue = asyncio.Queue()
        self._task = None
        self._language = language
        self._recognizer = recognizer_path or self.RECOGNIZER   # <— use provided or fallback

        bus.subscribe("client.audio", self.on_audio_chunk)
        print(f"GoogleSTT instance created for client {client_id}")

    async def on_audio_chunk(self, event: ClientAudio):
        """Callback to handle incoming audio chunks from the event bus."""
        if event.client_id == self.client_id:
            print(f"📥 Received audio chunk for client {self.client_id}, size: {len(event.chunk)} bytes")
            await self._audio_queue.put(event.chunk)

    async def _requests_generator(self) -> AsyncGenerator[cloud_speech.StreamingRecognizeRequest, None]:
        """Async generator for creating Google Cloud Speech streaming requests."""
        explicit_config = cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            audio_channel_count=1,
        )
        config = cloud_speech.RecognitionConfig(
            explicit_decoding_config=explicit_config,
            language_codes=["et-EE"],
            model="chirp_3", # Using chirp model
        )
        streaming_config = cloud_speech.StreamingRecognitionConfig(config=config, streaming_features=cloud_speech.StreamingRecognitionFeatures(interim_results=True))

        # First request contains the configuration
        yield cloud_speech.StreamingRecognizeRequest(
            recognizer=self.RECOGNIZER, streaming_config=streaming_config
        )

        # Subsequent requests contain the audio data
        while True:
            chunk = await self._audio_queue.get()
            if chunk is None:
                break
            yield cloud_speech.StreamingRecognizeRequest(audio=chunk)

    async def start(self):
        """Starts the STT process."""
        print(f"Starting Google STT for client {self.client_id}...")
        self._task = asyncio.create_task(self._run_stt())

    async def stop(self):
        """Stops the STT process."""
        print(f"Stopping Google STT for client {self.client_id}...")
        bus.subscribe("client.audio", self.on_audio_chunk)
        if self._task:
            await self._audio_queue.put(None) # Signal the end of the audio stream
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"Google STT stopped for client {self.client_id}.")


    async def _run_stt(self):
        """The main loop for the STT process."""
        try:
            responses = await  self._client.streaming_recognize(requests=self._requests_generator())

            async for response in responses:
                if not response.results:
                    continue

                for result in response.results:
                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript
                    if result.is_final:
                        print(f"✅ Final transcript for {self.client_id}: {transcript}")
                        await bus.publish(
                            "stt.final",
                            STTFinal(
                                text=transcript,
                                client_id=self.client_id,
                                start_ms=0, # start_ms and end_ms are not provided by the API in this mode
                                end_ms=0
                            ),
                        )
                    else:
                        print(f"🕓 Interim transcript for {self.client_id}: {transcript}", end="\r", flush=True)
                        await bus.publish(
                            "stt.partial",
                            STTPartial(
                                text=transcript,
                                client_id=self.client_id,
                                start_ms=0,
                                end_ms=0
                            ),
                        )
        except asyncio.CancelledError:
            print(f"STT process for {self.client_id} was cancelled.")
        except Exception as e:
            print(f"An error occurred in the STT process for client {self.client_id}: {e}")
        finally:
            print(f"STT process for {self.client_id} has ended.")

# This file is now a module, so the main guard is removed.
# The lifecycle of GoogleSTT will be managed by the WebSocket connection handler.
