import os

import pyaudio
from dotenv import load_dotenv
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech

load_dotenv()

# 🔐 Service account
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
RECOGNIZER_NAME = os.getenv("RECOGNIZER_NAME")

RECOGNIZER = f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/{RECOGNIZER_NAME}"

RATE = 8000
CHUNK = 100


def mic_stream():
    """Generator yielding small mic chunks for streaming_recognize()."""
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=None,
        stream_callback=None,
    )
    print("🎙️ Mic active. Speak now (Ctrl+C to stop)...\n")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield cloud_speech.StreamingRecognizeRequest(audio=data)
    except GeneratorExit:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


def main():
    client = speech_v2.SpeechClient(client_options={"api_endpoint": f"{LOCATION}-speech.googleapis.com"})

    explicit_config = cloud_speech.ExplicitDecodingConfig(
        encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        audio_channel_count=1,
    )

    config = cloud_speech.RecognitionConfig(
        explicit_decoding_config=explicit_config,
        language_codes=["et-EE"],
        model="chirp_3",
    )

    streaming_config = cloud_speech.StreamingRecognitionConfig(
        config=config,
    )

    config_request = cloud_speech.StreamingRecognizeRequest(
        recognizer=RECOGNIZER,
        streaming_config=streaming_config,
    )

    # ... (requests generator and response loop remain the same) ...
    def requests():
        yield config_request
        yield from mic_stream()

    responses = client.streaming_recognize(requests=requests())

    try:
        for response in responses:
            if not response.results:
                continue
            for result in response.results:
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    print(f"✅ Final: {transcript}")
                else:
                    print(f"🕓 Interim: {transcript}", end="\r", flush=True)
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")


if __name__ == "__main__":
    main()
