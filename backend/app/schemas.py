from pydantic import BaseModel


class PredictionResponse(BaseModel):
    text: str
    confidence: float
    language: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
