import json
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Tuple

import cv2
import mediapipe as mp
import numpy as np

from .config import DEFAULT_MODEL_PATH, FRAME_SIZE, LABEL_MAP_PATH, MAX_SEQUENCE_LENGTH, WORDS_TO_HINDI

try:
    import tensorflow as tf
except Exception:  # pragma: no cover
    tf = None


class GestureModelService:
    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH) -> None:
        self.model_path = model_path
        self.label_map = self._load_label_map()
        self.index_to_label = {int(v): k for k, v in self.label_map.items()}
        self.sequence: Deque[np.ndarray] = deque(maxlen=MAX_SEQUENCE_LENGTH)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.model = self._load_model()

    def _load_model(self):
        if tf is None or not self.model_path.exists():
            return None
        return tf.keras.models.load_model(self.model_path)

    def _load_label_map(self) -> Dict[str, int]:
        if LABEL_MAP_PATH.exists():
            return json.loads(LABEL_MAP_PATH.read_text())
        default_labels = [
            "hello",
            "thank_you",
            "yes",
            "no",
            "please",
            "A",
            "B",
            "C",
        ]
        return {label: idx for idx, label in enumerate(default_labels)}

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def extract_landmarks(self, frame: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        if not result.multi_hand_landmarks:
            return np.array([])

        hand_landmarks = result.multi_hand_landmarks[0]
        flat = []
        for lm in hand_landmarks.landmark:
            flat.extend([lm.x, lm.y, lm.z])
        return np.array(flat, dtype=np.float32)

    def _heuristic_predict(self, landmarks: np.ndarray) -> Tuple[str, float]:
        if landmarks.size == 0:
            return "", 0.0

        wrist_y = landmarks[1]
        index_tip_y = landmarks[8 * 3 + 1]
        thumb_tip_x = landmarks[4 * 3]
        pinky_tip_x = landmarks[20 * 3]
        openness = abs(pinky_tip_x - thumb_tip_x)

        if index_tip_y < wrist_y and openness > 0.25:
            return "hello", 0.66
        if index_tip_y < wrist_y and openness <= 0.25:
            return "yes", 0.61
        if index_tip_y >= wrist_y and openness <= 0.18:
            return "no", 0.58
        return "please", 0.52

    def _model_predict(self) -> Tuple[str, float]:
        if self.model is None or len(self.sequence) < MAX_SEQUENCE_LENGTH:
            return "", 0.0
        seq = np.array(self.sequence, dtype=np.float32)
        seq = np.expand_dims(seq, axis=0)
        pred = self.model.predict(seq, verbose=0)[0]
        idx = int(np.argmax(pred))
        return self.index_to_label.get(idx, ""), float(pred[idx])

    def predict(self, frame: np.ndarray, language: str = "en") -> Tuple[str, float]:
        landmarks = self.extract_landmarks(frame)
        if landmarks.size == 0:
            return "", 0.0

        self.sequence.append(landmarks)
        label, confidence = self._model_predict()
        if not label:
            label, confidence = self._heuristic_predict(landmarks)

        if language == "hi" and label in WORDS_TO_HINDI:
            return WORDS_TO_HINDI[label], confidence
        return label, confidence

    def predict_video_file(self, file_path: Path, language: str = "en") -> List[Dict[str, float]]:
        cap = cv2.VideoCapture(str(file_path))
        outputs: List[Dict[str, float]] = []
        frame_idx = 0
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            frame_idx += 1
            if frame_idx % 3 != 0:
                continue
            label, confidence = self.predict(frame, language=language)
            if label:
                outputs.append({"text": label, "confidence": round(confidence, 3)})
        cap.release()
        return outputs
