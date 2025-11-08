# Estonian-Language AI Voice Agent for the Service Sector

This project is an AI-powered voice agent designed to handle customer calls for service-based businesses in Estonia. It leverages cutting-edge AI technologies to provide a natural, human-like conversational experience in real-time.

## The Problem

Service companies such as car repair shops, beauty salons, and dental clinics often lose customers because they are unable to answer all incoming calls. The high cost of human labor makes providing 24/7 customer service prohibitively expensive for most small businesses.

## The Solution

We have developed an Estonian-language AI voice agent that answers customer calls in real-time with a human-like voice. The agent's "brain" is the **Gemma-3-27B** model, which understands customer requests, provides price estimates, and analyzes previous conversations to improve service.

### Key Capabilities

The voice agent is able to:
*   Receive calls and converse in natural Estonian.
*   Initiate bookings for services (e.g., oil changes, tire rotations, dental appointments), which are then approved by a human agent.
*   Provide price ranges and answer frequently asked questions.
*   Forward complex cases to a human agent for review in an admin view.

## Technical Implementation

The system is built on a modern, real-time technology stack to ensure low latency (< 1 second):

*   **Loveable**: Helped create the frontend interface.
*   **Google STT v2 (et-EE)**: Transcribes the customer's speech into text.
*   **Gemma-3-27B**: Understands the context of the conversation and generates appropriate responses.
*   **ElevenLabs v3 TTS (Estonian)**: Converts the agent's text responses into natural, emotional speech.

## Market Potential

There are thousands of service businesses in Estonia that require 24/7 phone availability. While an average customer service representative costs approximately €1500-€2000 per month, our AI-based voice agent can provide uninterrupted service for just **€10-€15 per day**.

There is also significant potential for expansion into the **Nordic and Baltic** regions, where other small service businesses are looking for affordable and automated solutions.

## Advantages

*   **Fully Estonian**: The first real-time AI voice agent that sounds just like a native Estonian speaker.
*   **Easy Integration**: Can be easily integrated with existing booking and billing systems via API.
*   **Scalable**: Suitable for a wide range of service industries, from auto repair to dentistry.

## Getting Started

Follow these instructions to run the project locally.

### Backend

To run the backend server, navigate to the `backend` directory and run the following command:

```shell
# From inside the 'backend' directory
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

To run the frontend application, navigate to the correct directory and run the development server:

```shell
# Navigate to the frontend directory
npm run dev
```

### Infrastructure

The models for this project run on a high-performance compute environment generously provided by **Datacrunch**, featuring 8x Nvidia A100 GPUs. Please refer to the provided shell scripts for configuration details.

### Screenshots
<img width="1171" height="1004" alt="image" src="https://github.com/user-attachments/assets/b95e740a-3dd1-40d7-b652-3f998910b974" />
<img width="1030" height="1030" alt="image" src="https://github.com/user-attachments/assets/f652cbbd-d8b9-4df2-8a16-5dd87fb02550" />
<img width="1031" height="1036" alt="image" src="https://github.com/user-attachments/assets/0334a3a1-b3b5-4bae-a7c5-cefcb8ad08a2" />


