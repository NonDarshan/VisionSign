"""Training script for lightweight ISL sequence model.

Expected dataset layout:
model/dataset/
  hello/*.npy
  thank_you/*.npy
  ...
Each .npy file should be (T, 63) landmarks where T <= 20.
"""

import json
from pathlib import Path

import numpy as np
import tensorflow as tf

MAX_LEN = 20
FEATURES = 63
MODEL_OUT = Path(__file__).resolve().parent / "isl_cnn_lstm.keras"
LABEL_MAP_PATH = Path(__file__).resolve().parent / "label_map.json"
DATASET_DIR = Path(__file__).resolve().parent / "dataset"


def load_dataset():
    label_map = json.loads(LABEL_MAP_PATH.read_text())
    X, y = [], []
    for label, idx in label_map.items():
        for file in (DATASET_DIR / label).glob("*.npy"):
            seq = np.load(file)
            padded = np.zeros((MAX_LEN, FEATURES), dtype=np.float32)
            length = min(MAX_LEN, seq.shape[0])
            padded[:length] = seq[:length]
            X.append(padded)
            y.append(idx)
    return np.array(X), tf.keras.utils.to_categorical(np.array(y), num_classes=len(label_map))


def build_model(num_classes: int) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(MAX_LEN, FEATURES))
    x = tf.keras.layers.Conv1D(64, 3, activation="relu", padding="same")(inp)
    x = tf.keras.layers.MaxPool1D()(x)
    x = tf.keras.layers.LSTM(64)(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    out = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inp, out)
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model


if __name__ == "__main__":
    X, y = load_dataset()
    if len(X) == 0:
        raise RuntimeError("No training samples found in model/dataset")

    model = build_model(y.shape[1])
    model.fit(X, y, validation_split=0.2, epochs=30, batch_size=16)
    model.save(MODEL_OUT)
    print(f"Saved model to: {MODEL_OUT}")
