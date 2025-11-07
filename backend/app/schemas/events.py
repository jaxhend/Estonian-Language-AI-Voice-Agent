from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import UUID

class ClientAudio(BaseModel):
    chunk: bytes
    encoding: Literal["pcm_s16le"] = "pcm_s16le"
    sr: int = 16000
    client_id: UUID

class STTPartial(BaseModel):
    text: str
    is_final: bool = False
    start_ms: int
    end_ms: int
    client_id: UUID

class STTFinal(BaseModel):
    text: str
    is_final: bool = True
    start_ms: int
    end_ms: int
    client_id: UUID

class ManagerRoute(BaseModel):
    intent: str
    agents: List[str]
    client_id: UUID

class AgentRequest(BaseModel):
    agent: str
    text: str
    context: dict = Field(default_factory=dict)
    client_id: UUID

class AgentUpdate(BaseModel):
    agent: str
    text: str
    client_id: UUID

class AgentResult(BaseModel):
    agent: str
    result: dict
    confidence: float
    client_id: UUID

class ManagerAnswer(BaseModel):
    text: str
    trace_id: str
    client_id: UUID

class TTSAudio(BaseModel):
    chunk: bytes
    mime: Literal["audio/mpeg"] = "audio/mpeg"
    client_id: UUID

class Error(BaseModel):
    code: int
    message: str
    client_id: UUID

