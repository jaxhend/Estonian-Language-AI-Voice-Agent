from dotenv import load_dotenv
import os

# To add your API key, you can either set it as an environment variable
# before running the server (e.g., `export ELEVENLABS_API_KEY="your_key"`),
# or you can hardcode it here for simplicity during testing.

# Method 1: Get from environment variable (recommended)
#ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Method 2: Hardcode the key (uncomment the line below and paste your key)
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY is not set. TTS will not work.")

