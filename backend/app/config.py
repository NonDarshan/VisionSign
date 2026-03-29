from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "model"
DEFAULT_MODEL_PATH = MODEL_DIR / "isl_cnn_lstm.keras"
LABEL_MAP_PATH = MODEL_DIR / "label_map.json"
MAX_SEQUENCE_LENGTH = 20
FRAME_SIZE = (224, 224)

WORDS_TO_HINDI = {
    "hello": "नमस्ते",
    "thank_you": "धन्यवाद",
    "yes": "हाँ",
    "no": "नहीं",
    "please": "कृपया",
}
