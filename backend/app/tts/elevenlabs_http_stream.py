# app/tts/elevenlabs_http_stream.py
import aiohttp
from app.bus import bus
from app.schemas.events import ManagerAnswer, TTSAudio


class ElevenLabsHTTPStream:
    """
    Simple ElevenLabs TTS HTTP streaming for short messages.
    Uses the /stream endpoint to get audio chunks directly.
    """
    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model_id: str = "eleven_v3",
        language_code: str = "et",
        stability: float = 0.5,
        output_format: str = "mp3_44100_64",
    ):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.language_code = language_code
        self.stability = stability
        self.output_format = output_format

    async def stream(self, event: ManagerAnswer):
        """
        Stream audio from ElevenLabs API directly to the client.
        """
        from app.api.ws import active_connections

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        if self.output_format:
            url += f"?output_format={self.output_format}"

        headers = {
            "xi-api-key": self.api_key,
            "Accept": "application/octet-stream",
            "Content-Type": "application/json",
        }

        body = {
            "text": event.text,
            "model_id": self.model_id,
            "language_code": self.language_code,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": 0.75,
            },
        }

        print(f"🔊 Starting TTS stream for client {event.client_id}: '{event.text}'")
        print(f"   Voice ID: {self.voice_id}")
        print(f"   Model: {self.model_id}")
        print(f"   Language: {self.language_code}")
        print(f"   Output Format: {self.output_format}")
        print(f"   Stability: {self.stability}")
        print(f"   URL: {url}")

        try:
            timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=body) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"❌ ElevenLabs API error {resp.status}: {error_text}")
                        return

                    print(f"✅ TTS stream started for client {event.client_id}")

                    # Stream the audio chunks to the client
                    chunk_count = 0
                    async for chunk in resp.content.iter_chunked(8192):
                        if chunk:
                            chunk_count += 1
                            # Stream each chunk to frontend
                            await bus.publish(
                                "tts.audio",
                                TTSAudio(
                                    chunk=chunk,
                                    client_id=event.client_id
                                )
                            )
                            if chunk_count <= 3:
                                print(f"🎵 Sent audio chunk #{chunk_count}, size: {len(chunk)} bytes")

                    print(f"🎵 TTS stream completed for client {event.client_id}, total chunks: {chunk_count}")

                    # ✅ Send the assistant text and final signal
                    if event.client_id in active_connections:
                        await active_connections[event.client_id].send_json({
                            "client_id": str(event.client_id),
                            "role": "assistant",
                            "text": event.text,
                            "isFinal": True
                        })

                    # ✅ Also publish to bus (so any other subscribers can use it)
                    await bus.publish(
                        "tts.audio",
                        TTSAudio(
                            chunk=b"",
                            client_id=event.client_id,
                            text=event.text,
                            is_final=True
                        )
                    )

        except Exception as e:
            print(f"❌ TTS streaming error for client {event.client_id}: {e}")

