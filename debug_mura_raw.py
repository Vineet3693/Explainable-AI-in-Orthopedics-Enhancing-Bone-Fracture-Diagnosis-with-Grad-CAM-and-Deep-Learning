import os
import tensorflow as tf
import numpy as np
from PIL import Image

models_path = r"D:\Coding Workspace\fracture detection ai\mura dataset kaggle results\models"
test_img_path = r"D:\Coding Workspace\fracture detection ai\data\raw\FracAtlas\images\Fractured\IMG0000019.jpg"

def focal_loss(alpha=0.25, gamma=2.0):
    def loss_fn(y_true, y_pred):
        return tf.keras.losses.binary_crossentropy(y_true, y_pred)
    return loss_fn

def inspect_model(model_name, filename, input_size):
    print(f"\n{'='*50}\nInspecting {model_name}...\n{'='*50}")
    model_file = os.path.join(models_path, filename)
    
    try:
        model = tf.keras.models.load_model(model_file, custom_objects={'loss_fn': focal_loss()})
        print(f"✅ Loaded successfully.")
        
        # Print input shape to verify what the model actually expects
        print(f"Expected Input Shape: {model.input_shape}")
        
        # Test 1: Standard preprocessing (used in app_mura.py)
        img = Image.open(test_img_path).convert("RGB")
        img_resized = img.resize((input_size, input_size))
        
        # Test A: Normalized [0, 1]
        arr_norm = np.array(img_resized, dtype=np.float32) / 255.0
        arr_norm = np.expand_dims(arr_norm, axis=0)
        pred_norm = model.predict(arr_norm, verbose=0)[0][0]
        
        # Test B: Not normalized [0, 255] (VGG sometimes expects this with its own preprocess_input)
        arr_unnorm = np.array(img_resized, dtype=np.float32)
        arr_unnorm = np.expand_dims(arr_unnorm, axis=0)
        pred_unnorm = model.predict(arr_unnorm, verbose=0)[0][0]
        
        # Test C: Keras preprocessing functions
        if "VGG" in model_name:
            arr_keras = tf.keras.applications.vgg16.preprocess_input(np.copy(arr_unnorm))
            pred_keras = model.predict(arr_keras, verbose=0)[0][0]
        elif "EfficientNet" in model_name:
            arr_keras = tf.keras.applications.efficientnet.preprocess_input(np.copy(arr_unnorm))
            pred_keras = model.predict(arr_keras, verbose=0)[0][0]
        else:
            pred_keras = "N/A"
            
        print(f"\nRaw Predictions for {model_name}:")
        print(f"  1. Normalized [0, 1] (Current App): {pred_norm:.4f}")
        print(f"  2. Unnormalized [0, 255]:         {pred_unnorm:.4f}")
        print(f"  3. Keras preprocess_input:        {pred_keras if isinstance(pred_keras, str) else f'{pred_keras:.4f}'}")
        
    except Exception as e:
        print(f"❌ Error loading or running model: {e}")

if __name__ == "__main__":
    inspect_model("EfficientNetB0", "EfficientNetB0.keras", 224)
    inspect_model("EfficientNetB1", "EfficientNetB1.keras", 240)
    inspect_model("VGG16", "VGG16.keras", 224)
