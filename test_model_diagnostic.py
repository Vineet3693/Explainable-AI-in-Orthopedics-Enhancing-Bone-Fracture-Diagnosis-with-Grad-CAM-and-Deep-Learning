"""
Model Diagnostic Script
Tests the model with different images to identify prediction bias
"""

import numpy as np
from PIL import Image
import tensorflow as tf
from pathlib import Path

# Load model
MODEL_PATH = "models/fracatlas/efficientnet_b0_final.h5"
print(f"Loading model from {MODEL_PATH}...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print(f"✅ Model loaded successfully!")
print(f"Model input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")

# Test images
test_images = [
    "data/raw/FracAtlas/images/Fractured/IMG0000019.jpg",
    "data/raw/FracAtlas/images/Fractured/IMG0000020.jpg",
    "data/raw/FracAtlas/images/Non-fractured/IMG0000001.jpg",
    "data/raw/FracAtlas/images/Non-fractured/IMG0000002.jpg",
]

print("\n" + "="*80)
print("TESTING MODEL PREDICTIONS")
print("="*80)

for img_path in test_images:
    if not Path(img_path).exists():
        print(f"⚠️  Image not found: {img_path}")
        continue
    
    # Preprocess
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    raw_output = model.predict(img_array, verbose=0)
    raw_score = float(raw_output[0][0])
    
    # Determine prediction
    is_fractured = raw_score > 0.5
    prediction = "Fractured" if is_fractured else "Non-Fractured"
    confidence = raw_score if is_fractured else (1.0 - raw_score)
    
    # Get expected label from path
    expected = "Fractured" if "Fractured" in img_path else "Non-Fractured"
    correct = "✅" if prediction == expected else "❌"
    
    print(f"\n{correct} Image: {Path(img_path).name}")
    print(f"   Expected: {expected}")
    print(f"   Predicted: {prediction}")
    print(f"   Raw Score: {raw_score:.6f}")
    print(f"   Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
    print(f"   Threshold: 0.5")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)

# Test with random noise to see if model is stuck
print("\nTesting with random noise...")
random_img = np.random.rand(1, 224, 224, 3).astype(np.float32)
random_output = model.predict(random_img, verbose=0)[0][0]
print(f"Random noise prediction: {random_output:.6f}")

# Test with all zeros
zeros_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
zeros_output = model.predict(zeros_img, verbose=0)[0][0]
print(f"All zeros prediction: {zeros_output:.6f}")

# Test with all ones
ones_img = np.ones((1, 224, 224, 3), dtype=np.float32)
ones_output = model.predict(ones_img, verbose=0)[0][0]
print(f"All ones prediction: {ones_output:.6f}")

print("\n" + "="*80)
if abs(random_output - zeros_output) < 0.01 and abs(random_output - ones_output) < 0.01:
    print("⚠️  MODEL IS STUCK! All inputs produce same output.")
    print("   This indicates the model is not properly trained.")
    print("   Recommendation: Retrain the model or use a different checkpoint.")
else:
    print("✅ Model responds to different inputs.")
    print("   Issue might be with preprocessing or threshold.")
print("="*80)
