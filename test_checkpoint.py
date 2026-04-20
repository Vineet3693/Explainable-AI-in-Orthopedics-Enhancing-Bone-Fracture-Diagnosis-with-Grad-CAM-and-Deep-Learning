"""
Test Phase2 Checkpoint Model
Verify if checkpoint_best.h5 from phase2 is properly trained
"""

import numpy as np
from PIL import Image
import tensorflow as tf
from pathlib import Path

# Test the recommended checkpoint
MODEL_PATH = "checkpoints/fracatlas/efficientnet_b0/phase2/checkpoint_best.h5"
print(f"Loading model from {MODEL_PATH}...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print(f"✅ Model loaded successfully!")
print(f"Model input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")

# Test images
test_images = [
    ("data/raw/FracAtlas/images/Fractured/IMG0000019.jpg", "Fractured"),
    ("data/raw/FracAtlas/images/Fractured/IMG0000020.jpg", "Fractured"),
    ("data/raw/FracAtlas/images/Non-fractured/IMG0000001.jpg", "Non-Fractured"),
    ("data/raw/FracAtlas/images/Non-fractured/IMG0000002.jpg", "Non-Fractured"),
]

print("\n" + "="*80)
print("TESTING PHASE2 CHECKPOINT MODEL")
print("="*80)

predictions = []
for img_path, expected in test_images:
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
    
    correct = "✅" if prediction == expected else "❌"
    predictions.append(raw_score)
    
    print(f"\n{correct} Image: {Path(img_path).name}")
    print(f"   Expected: {expected}")
    print(f"   Predicted: {prediction}")
    print(f"   Raw Score: {raw_score:.6f}")
    print(f"   Confidence: {confidence:.4f} ({confidence*100:.2f}%)")

print("\n" + "="*80)
print("TESTING WITH SYNTHETIC INPUTS")
print("="*80)

# Test with random noise
random_img = np.random.rand(1, 224, 224, 3).astype(np.float32)
random_output = model.predict(random_img, verbose=0)[0][0]
print(f"\nRandom noise prediction: {random_output:.6f}")

# Test with all zeros
zeros_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
zeros_output = model.predict(zeros_img, verbose=0)[0][0]
print(f"All zeros prediction: {zeros_output:.6f}")

# Test with all ones
ones_img = np.ones((1, 224, 224, 3), dtype=np.float32)
ones_output = model.predict(ones_img, verbose=0)[0][0]
print(f"All ones prediction: {ones_output:.6f}")

print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)

# Check variance in predictions
if len(predictions) > 0:
    variance = np.var(predictions)
    mean = np.mean(predictions)
    print(f"\nPrediction Statistics:")
    print(f"  Mean: {mean:.6f}")
    print(f"  Variance: {variance:.6f}")
    print(f"  Min: {min(predictions):.6f}")
    print(f"  Max: {max(predictions):.6f}")
    print(f"  Range: {max(predictions) - min(predictions):.6f}")

# Check if model is stuck
synthetic_variance = np.var([random_output, zeros_output, ones_output])
if variance < 0.001 and synthetic_variance < 0.001:
    print("\n❌ MODEL IS STILL STUCK!")
    print("   All inputs produce nearly identical outputs.")
    print("   This checkpoint is also not properly trained.")
elif variance < 0.01:
    print("\n⚠️  MODEL HAS LOW VARIANCE")
    print("   Predictions vary slightly but may still have issues.")
    print("   Consider testing other checkpoints or retraining.")
else:
    print("\n✅ MODEL IS WORKING!")
    print("   Predictions vary appropriately for different inputs.")
    print("   This checkpoint appears to be properly trained.")

print("="*80)
