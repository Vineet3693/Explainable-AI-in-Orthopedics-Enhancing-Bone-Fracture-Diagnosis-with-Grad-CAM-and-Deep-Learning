import tensorflow as tf
import os

MODEL_PATH = "models/fracatlas/efficientnet_b0_final.h5"

if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("Layer Names:")
    for layer in model.layers:
        if 'conv' in layer.name or 'conv2d' in layer.name:
            last_conv_layer = layer.name
    print(f"Likely last conv layer: {last_conv_layer}")
    
    # Also list the last few layers to be sure
    print("\nLast 10 layers:")
    for layer in model.layers[-10:]:
        print(layer.name)
