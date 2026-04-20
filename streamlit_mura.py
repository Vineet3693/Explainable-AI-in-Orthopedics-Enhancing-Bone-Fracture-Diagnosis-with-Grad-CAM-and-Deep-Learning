import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="MURA Fracture AI",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# Custom CSS for Premium Glassmorphic Look
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Glassmorphism Containers */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .prediction-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .status-fractured {
        color: #ef4444;
        font-weight: bold;
    }

    .status-normal {
        color: #10b981;
        font-weight: bold;
    }

    /* Metrics Styling */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #94a3b8;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# API Helper Functions
# ──────────────────────────────────────────────
API_BASE_URL = "http://127.0.0.1:8001"

def fetch_models():
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/models", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return None

def perform_prediction(file_bytes, model_name=None):
    try:
        files = {"file": file_bytes}
        params = {"model_name": model_name} if model_name else {}
        response = requests.post(f"{API_BASE_URL}/api/v1/predict", files=files, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Failed to connect to API"}

# ──────────────────────────────────────────────
# Sidebar - Configuration
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1 style='color: #38bdf8;'>🦴 MURA AI Settings</h1>", unsafe_allow_html=True)
    
    models_data = fetch_models()
    
    if models_data and "error" not in models_data:
        model_names = ["Ensemble (Recommended)"] + [m['name'] for m in models_data['models']]
        
        # Determine default index (highlight VGG16 if ensemble not selected)
        default_idx = 0
        
        selected_model_option = st.selectbox(
            "Select Detection Model",
            options=model_names,
            index=default_idx,
            help="VGG16 is currently the highest performing single model (77% accuracy)."
        )
        
        actual_model_name = None if "Ensemble" in selected_model_option else selected_model_option
        
        st.markdown("---")
        st.subheader("📊 Model Performance")
        
        if actual_model_name:
            # Show metrics for selected model
            model_info = next((m for m in models_data['models'] if m['name'] == actual_model_name), None)
            if model_info:
                st.write(f"**Accuracy:** {model_info['accuracy']:.1%}")
                st.write(f"**F1-Score:** {model_info['f1_score']:.2f}")
                st.write(f"**AUC:** {model_info['auc']:.2f}")
                st.write(f"**Params:** {model_info['params']}")
        else:
            st.write("Using ensemble average across all 3 models for maximum robustness.")
            st.info("Ensuring high specificity for clinical reliability.")
    else:
        error_msg = models_data.get("error") if models_data else "Unknown connection error"
        st.error(f"⚠️ API Offline. Error: {error_msg}")
        st.info("Please ensure `app_mura.py` is running on port 8001.")
        selected_model_option = "Ensemble (Recommended)" 
        actual_model_name = None

    st.markdown("---")
    st.markdown("### 🏥 About MURA")
    st.caption("MURA (Musculoskeletal Radiographs) is a large dataset for abnormality detection in musculoskeletal radiographs.")
    st.image("https://img.icons8.com/isometric/100/hospital.png", width=50)

# ──────────────────────────────────────────────
# Main UI
# ──────────────────────────────────────────────
st.markdown("<div class='prediction-header'>🏥 MURA Fracture Detection Dashboard</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Upload an X-ray image to identify fractures using state-of-the-art MURA-trained models.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📷 Uploaded X-ray")
        st.image(uploaded_file, use_container_width=True)
        
        if st.button("🚀 Analyze Now", type="primary", use_container_width=True):
            with st.spinner("Processing through neural networks..."):
                result = perform_prediction(uploaded_file.getvalue(), actual_model_name)
                st.session_state['mura_result'] = result
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if 'mura_result' in st.session_state:
            res = st.session_state['mura_result']
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                
                # Result Header
                is_fractured = res['final_result'] == "Fractured"
                status_class = "status-fractured" if is_fractured else "status-normal"
                icon = "🚨" if is_fractured else "✅"
                
                st.markdown(f"<h2>{icon} <span class='{status_class}'>{res['final_result'].upper()}</span></h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 1.2rem;'>Confidence: <b>{res['final_confidence']:.1%}</b></p>", unsafe_allow_html=True)
                
                # Progress bar for confidence
                st.progress(res['final_confidence'])
                
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                
                # Recommendation
                st.info(f"**Recommendation:** {res['recommendation']}")
                
                # Model Breakdown
                with st.expander("🔍 Detailed Model Breakdown"):
                    preds = res.get('individual_predictions', [])
                    if preds:
                        df = pd.DataFrame([
                            {
                                "Model": p['model'],
                                "Prediction": p['prediction'],
                                "Confidence": f"{p['confidence']:.1%}",
                                "Accuracy": f"{p['metrics']['accuracy']:.1%}"
                            } for p in preds
                        ])
                        st.table(df)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='glass-card' style='text-align: center; padding: 60px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #475569;'>Analysis Results Pending</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748b;'>Upload an image and click <b>Analyze Now</b> to see the AI diagnosis.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Comparison Table
# ──────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Model Comparison")
if models_data and "models" in models_data:
    comparison_df = pd.DataFrame([
        {
            "Model Name": m['name'],
            "Accuracy": m['accuracy'],
            "Precision": m['precision'],
            "Recall": m['recall'],
            "F1-Score": m['f1_score'],
            "Params": m['params']
        } for m in models_data['models']
    ])
    st.dataframe(comparison_df.style.highlight_max(axis=0, subset=['Accuracy', 'F1-Score', 'Precision', 'Recall'], color='#1e3a8a'), use_container_width=True)
else:
    st.info("Start the API to see model comparison data.")

# Footer
st.markdown("<div style='text-align: center; color: #64748b; margin-top: 50px; padding: 20px;'>MURA Fracture Detection AI v2.0 • Powered by TensorFlow & Streamlit</div>", unsafe_allow_html=True)
