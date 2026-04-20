import os
# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from pathlib import Path

BASE_DIR = Path(r"d:\Coding Workspace\fracture detection ai")
MODEL_PATH = BASE_DIR / "mura dataset kaggle results" / "models" / "VGG16.keras"

if not MODEL_PATH.exists():
    print(f"ERROR: Model not found at {MODEL_PATH}")
    exit(1)

print(f"Loading model from {MODEL_PATH}...")
try:
    model = tf.keras.models.load_model(str(MODEL_PATH))
    print("\n--- Model Summary ---")
    model.summary()

    print("\n--- Layer Details ---")
    for layer in model.layers:
        print(f"Layer: {layer.name}, Type: {type(layer).__name__}")
        if hasattr(layer, 'output_shape'):
            print(f"  Output Shape: {layer.output_shape}")

    print("\n--- Input Details ---")
    print(f"Input nodes: {model.inputs}")
    print(f"Input shape: {model.input_shape}")

except Exception as e:
    print(f"ERROR loading model: {e}")
