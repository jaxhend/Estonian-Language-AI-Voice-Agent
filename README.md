# Estonian-Language AI Voice Agent for the Service Sector

A real-time, AI-powered voice agent that provides natural, human-like customer service in Estonian, ensuring service businesses never miss a customer call.

## Watch it in Action

### 20-second Quick Demo
https://github.com/user-attachments/assets/6b456f8d-4fef-4092-a9b2-cd8b6a0f67b4

### 2-Minute Full Pitch & Demo
**[Watch the 2-Minute Pitch & Demo on YouTube](https://www.youtube.com/watch?v=gE2C2v7KWaQ)**  
A concise overview showcasing the voice agent’s concept, key features, and real-time performance in action.

## The Problem

Service companies such as car repair shops, beauty salons, and dental clinics often lose customers because they are unable to answer all incoming calls. The high cost of human labor makes providing 24/7 customer service prohibitively expensive for most small businesses.

## The Solution

We have developed an Estonian-language AI voice agent that answers customer calls in real-time with a human-like voice. The agent's "brain" is the **Gemma-3-27B** model, which understands customer requests, provides price estimates, and analyzes previous conversations to improve service.

### Key Capabilities

The voice agent is able to:
*   24/7 Call Handling: Answers calls instantly in natural, fluent Estonian.
*   Smart Booking: Initiates service bookings (e.g., oil changes, tire rotations, dental appointments) for later human approval.
*   Instant Answers: Provides price ranges and answers frequently asked questions.
*   Context-Aware: Maintains conversational context to provide personalized and efficient interactions.

## Technical Implementation

The system is engineered for **low latency (~2 seconds)** to enable natural, real-time conversational flow.
- **Frontend: Loveable** (Powers the responsive user interface)
- **AI "Brain": Gemma-3-27B** (Interprets context and generates responses)
- **Speech-to-Text (STT): Google STT v2 (et-EE)** (High-accuracy Estonian transcription)
- **Text-to-Speech (TTS): ElevenLabs v3 (Estonian)** (Natural, expressive voice generation)

## Market Potential

There are thousands of service businesses in Estonia that require 24/7 phone availability. While an average customer service representative costs approximately €1500-€2000 per month, our AI-based voice agent can provide uninterrupted service for just **€10-€15 per day**.

There is also significant potential for expansion into the **Nordic and Baltic** regions, where other small service businesses are looking for affordable and automated solutions.

## Advantages

*   **Fully Estonian**: The first real-time AI voice agent that sounds just like a native Estonian speaker.
*   **Easy Integration**: Designed for simple API integration with existing booking and billing systems.
*   **Scalable**: Flexible architecture suitable for any service industry, from auto repair to dentistry.

## Getting Started

Follow these instructions to run the project locally.

### Prerequisites
- Python 3.12
- Node.js and npm
- Google Cloud Service Account json (for STT v2)
- ElevenLabs API Key
- Access to a self-hosted LLM endpoint (for Gemma-3-27B)

### Backend

The backend server handles the core logic, STT, LLM, and TTS integrations.
#### 1. Navigate to the backend directory
```shell
cd backend
```

#### 2. Install dependencies
```shell
python -m pip install -r requirements.txt
```

#### 3. Create a `.env` file in the `/backend` directory

Populate it with your API keys and configuration values.

#### Sample `.env`
```shell
ELEVENLABS_API_KEY=.....
ELEVENLABS_VOICE_ID=tIFPE2y0DAU6xfZn3Fka
ELEVENLABS_MODEL=eleven_v3
ELEVENLABS_LANGUAGE=et
ELEVENLABS_LANG=et

LLM_URL=....
LLM_MODEL=google/gemma-3-27b-it
LLM_MAX_TOKENS=250
LLM_TIMEOUT_S=30
DB_URL=app/data/context_database.json
FAQ_URL=app/data/faq.json

GOOGLE_APPLICATION_CREDENTIALS=.....
PROJECT_ID=.....
LOCATION=europe-west3
RECOGNIZER_NAME=.....
```

#### 4. Run the backend server
```shell
# From inside the 'backend' directory
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Frontend

To run the frontend application:

#### 1. Navigate to the frontend directory
```shell
cd frontend
```

#### 2. Start the development server
```shell
npm install
npm run dev
```

## Infrastructure

The models for this project run on a high-performance compute environment.

**Provider:** Datacrunch  
**Hardware:** 8× Nvidia A100 GPUs (admittedly overkill for this use case)

For configuration details, refer to the shell scripts located in the `/llm` directory.


## Screenshots
<img width="1171" height="1004" alt="image" src="https://github.com/user-attachments/assets/b95e740a-3dd1-40d7-b652-3f998910b974" />
<img width="1030" height="1030" alt="image" src="https://github.com/user-attachments/assets/f652cbbd-d8b9-4df2-8a16-5dd87fb02550" />
<img width="1031" height="1036" alt="image" src="https://github.com/user-attachments/assets/0334a3a1-b3b5-4bae-a7c5-cefcb8ad08a2" />


