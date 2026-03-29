import asyncio
import base64
import tempfile
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .model_service import GestureModelService
from .schemas import HealthResponse

app = FastAPI(title="VisonSign API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = GestureModelService()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=service.is_model_loaded)


@app.post("/translate/video")
async def translate_video(
    file: UploadFile = File(...),
    language: str = Form("en"),
) -> Dict[str, Any]:
    suffix = Path(file.filename or "sample.mp4").suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        predictions = service.predict_video_file(tmp_path, language=language)
        transcript = " ".join(item["text"] for item in predictions)
        return {"predictions": predictions, "transcript": transcript}
    finally:
        tmp_path.unlink(missing_ok=True)


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            frame_b64 = data.get("frame")
            language = data.get("language", "en")
            if not frame_b64:
                await websocket.send_json({"text": "", "confidence": 0.0})
                continue

            decoded = base64.b64decode(frame_b64)
            arr = np.frombuffer(decoded, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"text": "", "confidence": 0.0})
                continue

            text, confidence = service.predict(frame, language=language)
            await websocket.send_json({"text": text, "confidence": round(confidence, 3)})
            await asyncio.sleep(0.001)
    except WebSocketDisconnect:
        return
