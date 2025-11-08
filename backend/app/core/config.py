# .env file should be in the /backend directory.

from dotenv import load_dotenv
import os

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL")
ELEVENLABS_LANGUAGE = os.getenv("ELEVENLABS_LANGUAGE")
ELEVENLABS_LANG = os.getenv("ELEVENLABS_LANG")

LLM_URL = os.getenv("LLM_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_MAX_TOKENS = os.getenv("LLM_MAX_TOKENS")
LLM_TIMEOUT_S = os.getenv("LLM_TIMEOUT_S")
DB_URL = os.getenv("DB_URL")

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
RECOGNIZER_NAME = os.getenv("RECOGNIZER_NAME")
