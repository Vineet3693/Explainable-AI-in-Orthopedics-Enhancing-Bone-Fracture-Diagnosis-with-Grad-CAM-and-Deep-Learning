import tensorflow as tf
import os

MODEL_PATH = "models/fracatlas/efficientnet_b0_final.h5"

def focal_loss(alpha=0.75, gamma=2.0):
    def loss_fn(y_true, y_pred):
        return tf.reduce_mean(y_true - y_pred)
    return loss_fn

print(f"TF Version: {tf.__version__}")
if os.path.exists(MODEL_PATH):
    print(f"Attempting to load model from {MODEL_PATH}...")
    try:
        # Try loading without custom objects first to see actual error
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("✅ Model loaded successfully (without compile)!")
        print(f"Model Inputs: {model.input_shape}")
        print(f"Model Outputs: {model.output_shape}")
        
        # Now try to compile it manually
        model.compile(optimizer='adam', loss=focal_loss())
        print("✅ Model compiled successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Model path {MODEL_PATH} does not exist.")
