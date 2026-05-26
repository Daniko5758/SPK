"""
SPK HIPERTENSION - Decision Tree Decision Support System
dengan Probability Calibration + Visualisasi Pohon Lengkap

Version: 2.0 (Calibrated)
"""

import streamlit as st
import joblib
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# Import utils
from utils.encode import get_valid_options, encode_to_model_input
from utils.tree_walker import get_decision_path
from utils.visualizer_v2 import plot_decision_path_only

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="SPK Hipertensi - Decision Tree",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .result-card.hypertension {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .result-card.normal {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .result-label {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .result-confidence {
        font-size: 3rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    .result-desc {
        font-size: 0.95rem;
        opacity: 0.9;
    }
    .step-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .step-number {
        background: #3498db;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 10px;
    }
    .step-feature {
        font-weight: 600;
        color: #2C3E50;
        font-size: 1.1rem;
    }
    .step-comparison {
        font-family: monospace;
        background: #ecf0f1;
        padding: 0.3rem 0.6rem; border-radius: 4px;
        margin-top: 0.3rem;
        display: inline-block;
    }
    .step-direction {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .direction-yes {
        background: #e74c3c;
        color: white;
    }
    .direction-no {
        background: #27ae60;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INISIALISASI (LOAD MODEL)
# ============================================================

@st.cache_resource
def initialize_model():
    """Load calibrated model + base tree untuk visualisasi"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, 'models')

        # Load calibrated model (untuk prediksi dengan confidence realistis)
        calibrated_model = joblib.load(os.path.join(models_dir, 'model_calibrated.joblib'))

        # Load base tree (untuk visualisasi & animated walk)
        base_tree = joblib.load(os.path.join(models_dir, 'base_tree.joblib'))

        # Load feature names
        with open(os.path.join(models_dir, 'feature_names.json'), 'r') as f:
            feature_names = json.load(f)

        # Load label mappings
        with open(os.path.join(models_dir, 'label_mappings.json'), 'r') as f:
            label_data = json.load(f)

        # Load training report
        with open(os.path.join(models_dir, 'training_report.txt'), 'r') as f:
            training_report = f.read()

        # Load tree visualization
        tree_img_path = os.path.join(models_dir, 'decision_tree_full.png')
        tree_img = Image.open(tree_img_path) if os.path.exists(tree_img_path) else None

        return {
            'calibrated_model': calibrated_model,
            'base_tree': base_tree,
            'feature_names': feature_names,
            'label_maps': label_data['label_maps'],
            'reverse_maps': label_data['reverse_maps'],
            'training_report': training_report,
            'tree_image': tree_img
        }
    except FileNotFoundError as e:
        return None


# ============================================================
# HEADER
# ============================================================

st.markdown('<p class="main-header">🏥 Sistem Pendukung Keputusan</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Deteksi Hipertensi - Decision Tree + Probability Calibration</p>', unsafe_allow_html=True)

# Load model
app_data = initialize_model()

if app_data is None:
    st.error("⚠️ Model tidak ditemukan! Jalankan dulu `python train_model.py`")
    st.stop()

calibrated_model = app_data['calibrated_model']
base_tree = app_data['base_tree']
feature_names = app_data['feature_names']
label_maps = app_data['label_maps']
reverse_maps = app_data['reverse_maps']

# ============================================================
# LAYOUT: 2 KOLOM
# ============================================================

col_form, col_result = st.columns([1, 1.2], gap="large")

# ============================================================
# KOLOM KIRI: FORM INPUT
# ============================================================

with col_form:
    st.markdown("### 📋 Input Data Pasien")

    with st.form(key="prediction_form", clear_on_submit=False):
        st.markdown("---")

        age = st.number_input("**Usia (Age)**", min_value=1, max_value=120, value=45)
        salt_intake = st.slider("**Asupan Garam (Salt Intake)** - gram/hari", 0.0, 25.0, 8.0, 0.5)
        stress_score = st.slider("**Tingkat Stres (Stress Score)**", 0, 10, 5)

        bp_options = list(label_maps['BP_History'].keys())
        bp_history = st.selectbox("**Riwayat Tekanan Darah (BP History)**", bp_options, index=0)

        sleep_duration = st.slider("**Durasi Tidur (Sleep Duration)** - jam/hari", 0.0, 24.0, 7.0, 0.5)
        bmi = st.number_input("**BMI (Body Mass Index)**", 10.0, 80.0, 25.0, 0.1)

        family_options = list(label_maps['Family_History'].keys())
        family_history = st.selectbox("**Riwayat Keluarga Hipertensi**", family_options, index=0)

        exercise_options = list(label_maps['Exercise_Level'].keys())
        exercise_level = st.selectbox("**Tingkat Aktivitas Fisik**", exercise_options, index=0)

        smoking_options = list(label_maps['Smoking_Status'].keys())
        smoking_status = st.selectbox("**Status Merokok**", smoking_options, index=0)

        st.markdown("---")
        submitted = st.form_submit_button("🔍 Jalankan Prediksi")

    footer_html = (
        '<div style="font-size: 0.8rem; color: #95a5a6; text-align: center; margin-top: 0.5rem;">'
        'Model: Decision Tree + Probability Calibration (Isotonic)<br>'
        'Training: 80% data, GridSearchCV tuned'
        '</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)


# ============================================================
# KOLOM KANAN: HASIL PREDIKSI
# ============================================================

with col_result:
    st.markdown("### 📊 Hasil Prediksi")

    if not submitted:
        st.info("👈 Silakan isi formulir dan klik **'Jalankan Prediksi'**")
    else:
        # Build input
        user_input = {
            'Age': age, 'Salt_Intake': salt_intake, 'Stress_Score': stress_score,
            'BP_History': bp_history, 'Sleep_Duration': sleep_duration, 'BMI': bmi,
            'Family_History': family_history, 'Exercise_Level': exercise_level,
            'Smoking_Status': smoking_status
        }

        # Encode
        X_input = encode_to_model_input(user_input, feature_names)
        X_array = np.array(X_input).reshape(1, -1)

        # Predict dengan CALIBRATED model (confidence realistis)
        predicted_class = int(calibrated_model.predict(X_array)[0])
        probabilities = calibrated_model.predict_proba(X_array)[0]
        confidence = float(np.max(probabilities))

        # Decode label
        pred_label = reverse_maps['Has_Hypertension'].get(
            predicted_class,
            "Hipertensi" if predicted_class == 1 else "Tidak Hipertensi"
        )

        # Get decision path dari BASE TREE (untuk visualisasi)
        path_info = get_decision_path(base_tree, X_array, raw_input=user_input)

        # === RESULT CARD ===
        card_class = "hypertension" if predicted_class == 1 else "normal"
        icon = "⚠️" if predicted_class == 1 else "✅"
        desc = "Disarankan konsultasi dokter" if predicted_class == 1 else "Tetap jaga pola hidup sehat"
        conf_pct_str = f"{float(confidence) * 100:.1f}"
        prob0_str = f"{float(probabilities[0]) * 100:.1f}"
        prob1_str = f"{float(probabilities[1]) * 100:.1f}"

        result_html = f'<div class="result-card {card_class}"><div class="result-label">{icon} {pred_label}</div>'
        result_html += f'<div class="result-confidence">{conf_pct_str}%</div>'
        result_html += f'<div class="result-desc"><b>Tingkat Keyakinan (Calibrated)</b><br>{desc}</div></div>'
        st.markdown(result_html, unsafe_allow_html=True)

        # Probability breakdown
        st.markdown("#### Probabilitas")
        prob_col1, prob_col2 = st.columns(2)
        with prob_col1:
            st.metric("Tidak Hipertensi", f"{prob0_str}%")
        with prob_col2:
            st.metric("Hipertensi", f"{prob1_str}%")

        # ============================================================
        # DECISION PATH VISUALIZATION (plot_tree style)
        # ============================================================

        st.markdown("#### Alur Keputusan (Decision Path - User Input)")

        # Buat visualisasi decision path dengan style plot_tree
        path_fig = plot_decision_path_only(path_info, reverse_maps, confidence=confidence)
        st.pyplot(path_fig)

        

# ============================================================
# BAGIAN BAWAH: VISUALISINFO MODEL
# ============================================================

st.markdown("---")
st.markdown("### 🌳 Visualisasi Pohon Keputusan Lengkap")

if app_data['tree_image']:
    st.image(app_data['tree_image'], caption="Decision Tree - Full Visualization", use_container_width=True)
else:
    st.warning("Visualisasi pohon belum tersedia. Jalankan `python train_model.py` untuk generate.")

st.markdown("---")
st.markdown("### 🧠 Informasi Model")

info_col1, info_col2 = st.columns([1, 1])

with info_col1:
    st.markdown("#### 📊 Feature Importance")

    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': base_tree.feature_importances_
    }).sort_values('Importance', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(importance_df)))
    bars = ax.barh(importance_df['Feature'], importance_df['Importance'], color=colors)

    for bar, val in zip(bars, importance_df['Importance']):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9)

    ax.set_xlabel('Importance Score')
    ax.set_title('Feature Importance', fontsize=14, fontweight='bold')
    ax.set_xlim(0, importance_df['Importance'].max() * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

    top3 = importance_df.tail(3).sort_values('Importance', ascending=False)
    st.markdown("**Top 3 Faktor:**")
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        st.markdown(f"  {i}. **{row['Feature']}** ({row['Importance']:.3f})")

with info_col2:
    st.markdown("#### 📄 Detail Model")

    st.json({
        "model_type": "CalibratedClassifierCV",
        "base_estimator": "DecisionTreeClassifier",
        "calibration_method": "isotonic",
        "criterion": base_tree.criterion,
        "max_depth": base_tree.max_depth,
        "min_samples_split": base_tree.min_samples_split,
        "min_samples_leaf": base_tree.min_samples_leaf,
        "n_features": base_tree.n_features_in_,
        "n_nodes": base_tree.tree_.node_count,
        "tree_depth": base_tree.get_depth()
    })

    with st.expander("📋 Laporan Training"):
        st.code(app_data['training_report'])

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
footer_html = (
    '<div style="text-align: center; color: #95a5a6; font-size: 0.85rem; padding: 1rem;">'
    'SPK Hipertensi v2.0 - Decision Tree + Probability Calibration<br>'
    'Sistem Pendukung Keputusan untuk Deteksi Hipertensi'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
