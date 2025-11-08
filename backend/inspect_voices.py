#!/usr/bin/env python3
"""
Test and list available ElevenLabs voices that support eleven_v3 model
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

async def list_voices():
    """List all available voices"""
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY is not set!")
        return

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ Error {resp.status}: {error_text}")
                    return

                data = await resp.json()
                voices = data.get("voices", [])

                print("\n" + "=" * 80)
                print("Available ElevenLabs Voices")
                print("=" * 80)

                for i, voice in enumerate(voices, 1):
                    voice_id = voice.get("voice_id")
                    name = voice.get("name")
                    category = voice.get("category", "unknown")
                    labels = voice.get("labels", {})

                    print(f"\n{i}. {name}")
                    print(f"   ID: {voice_id}")
                    print(f"   Category: {category}")
                    if labels:
                        print(f"   Labels: {labels}")

                    # Check if this is the current voice
                    current_voice = os.getenv("ELEVENLABS_VOICE_ID", "")
                    if voice_id == current_voice:
                        print(f"   ✓ THIS IS YOUR CURRENT VOICE")

                print("\n" + "=" * 80)
                print(f"Total voices: {len(voices)}")
                print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_voice_with_v3(voice_id: str, voice_name: str):
    """Test a specific voice with eleven_v3 model"""
    print(f"\nTesting voice '{voice_name}' with eleven_v3...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?output_format=mp3_44100_64"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Accept": "application/octet-stream",
        "Content-Type": "application/json",
    }

    body = {
        "text": "Tere! See on test eesti keeles.",
        "model_id": "eleven_v3",
        "language_code": "et",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    # Count the audio data
                    total_bytes = 0
                    async for chunk in resp.content.iter_chunked(8192):
                        total_bytes += len(chunk)
                    print(f"   ✅ SUCCESS! Generated {total_bytes} bytes of audio")
                    return True
                else:
                    error_text = await resp.text()
                    print(f"   ❌ FAILED: {resp.status} - {error_text}")
                    return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

async def main():
    print("🔍 ElevenLabs Voice Inspector")
    print("=" * 80)

    # List all voices
    await list_voices()

    # Test current voice
    current_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
    if current_voice_id:
        print(f"\n\n🧪 Testing your current voice with eleven_v3...")
        await test_voice_with_v3(current_voice_id, "Current Voice")

if __name__ == "__main__":
    asyncio.run(main())

