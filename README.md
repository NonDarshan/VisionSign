# VisonSign

VisonSign is a real-time **Indian Sign Language (ISL) interpreter** that converts hand gestures into text and speech.

## Features
- Real-time webcam gesture translation (WebSocket)
- ISL text output with confidence score
- English/Hindi output switching
- Text-to-speech output in browser
- Dark mode glassmorphism UI
- Offline video upload translation
- Translation history with local persistence
- Gesture guide/tutorial
- Modular model training pipeline for custom datasets

## Project Structure
```
frontend/   # React UI
backend/    # FastAPI + MediaPipe inference service
model/      # Label map and training script
utils/      # Helpers for future expansion
assets/     # Static assets
```

## Run Locally

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Train Custom Model
Place `.npy` landmark sequences in `model/dataset/<label>/`.

```bash
cd model
python train.py
```

This outputs `model/isl_cnn_lstm.keras` which the backend auto-loads if present.

## API Summary
- `GET /health` — service health + model load status
- `WS /ws/translate` — real-time frame-to-text translation
- `POST /translate/video` — translate uploaded video offline

## Notes for Accuracy
- Keep camera at chest/hand level
- Ensure good lighting and plain background
- Use consistent gesture speed
- For production, train with diverse ISL data and augmentations
