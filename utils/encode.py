"""
Utility: Label Encoding & Decoding
Fungsi untuk mengkonversi data input user ke format numerik yang dipahami model,
dan sebaliknya (decode hasil prediksi ke label yang readable).
"""

import json
import os

# Load mappings dari file
_models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')

def _load_mappings():
    """Load label mappings dari file JSON"""
    with open(os.path.join(_models_dir, 'label_mappings.json'), 'r') as f:
        data = json.load(f)
    return data['label_maps'], data['reverse_maps']

# ============================================================
# ENCODING: Konversi input user (string) ke numerik
# ============================================================

def encode_input(input_dict):
    """
    Encode input dictionary user ke format numerik untuk prediksi.

    Args:
        input_dict: dict dengan keys sesuai feature names
                    contoh: {'Age': 45, 'BP_History': 'Normal', ...}

    Returns:
        dict dengan semua nilai sudah di-encode ke numerik
    """
    label_maps, _ = _load_mappings()
    encoded = {}

    for feature, value in input_dict.items():
        if feature in label_maps:
            # Feature categorical: mapping string ke angka
            if value in label_maps[feature]:
                encoded[feature] = label_maps[feature][value]
            else:
                # Value tidak ada di mapping, coba sebagai angka
                try:
                    encoded[feature] = int(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value '{value}' untuk feature '{feature}'. "
                                   f"Opsi yang valid: {list(label_maps[feature].keys())}")
        else:
            # Feature numerik (Age, Salt_Intake, dst): langsung pakai
            encoded[feature] = float(value)

    return encoded


def encode_to_model_input(input_dict, feature_names):
    """
    Konversi input dict ke numpy array yang sesuai urutan feature_names.

    Args:
        input_dict: dict input user (bisa string atau numerik)
        feature_names: list nama fitur sesuai model

    Returns:
        numpy array 2D siap untuk model.predict()
    """
    encoded = encode_input(input_dict)
    return [encoded[feat] for feat in feature_names]


# ============================================================
# DECODING: Konversi hasil prediksi numerik ke label readable
# ============================================================

def decode_prediction(prediction, return_label=True):
    """
    Decode hasil prediksi numerik ke label yang readable.

    Args:
        prediction: 0 atau 1 (atau array [prob_0, prob_1])
        return_label: True -> return label string

    Returns:
        Jika return_label=True: ('Tidak Hipertensi' / 'Hipertensi', confidence)
        Jika return_label=False: (0 / 1, confidence)
    """
    _, reverse_maps = _load_mappings()

    pred_int = int(prediction[0]) if isinstance(prediction, (list, tuple, np.ndarray)) else int(prediction)
    label = reverse_maps['Has_Hypertension'].get(pred_int, str(pred_int))

    return label, pred_int


def get_confidence(probabilities):
    """
    Hitung tingkat keyakinan dari array probabilitas.

    Args:
        probabilities: array [prob_class_0, prob_class_1] dari model.predict_proba()

    Returns:
        float: confidence percentage
    """
    import numpy as np
    return float(np.max(probabilities) * 100)


# ============================================================
# VALIDASI INPUT
# ============================================================

def get_valid_options():
    """Return opsi valid untuk setiap feature kategorikal"""
    label_maps, _ = _load_mappings()
    return label_maps


def validate_input(input_dict):
    """
    Validasi input user sebelum diproses.
    Raise ValueError jika ada input yang tidak valid.

    Args:
        input_dict: dict input dari user
    """
    label_maps, _ = _load_mappings()

    for feature, value in input_dict.items():
        if feature in label_maps:
            # Feature kategorikal
            valid_options = list(label_maps[feature].keys())
            if value not in valid_options:
                raise ValueError(
                    f"Nilai '{value}' untuk '{feature}' tidak valid. "
                    f"Opsi yang tersedia: {valid_options}"
                )

    # Validasi range numerik
    if 'Age' in input_dict:
        age = float(input_dict['Age'])
        if not (0 < age <= 120):
            raise ValueError("Age harus antara 1 dan 120 tahun.")

    if 'BMI' in input_dict:
        bmi = float(input_dict['BMI'])
        if not (10 <= bmi <= 80):
            raise ValueError("BMI harus antara 10 dan 80.")

    if 'Salt_Intake' in input_dict:
        salt = float(input_dict['Salt_Intake'])
        if not (0 <= salt <= 25):
            raise ValueError("Salt Intake harus antara 0 dan 25 gram/hari.")

    if 'Stress_Score' in input_dict:
        stress = float(input_dict['Stress_Score'])
        if not (0 <= stress <= 10):
            raise ValueError("Stress Score harus antara 0 dan 10.")

    if 'Sleep_Duration' in input_dict:
        sleep = float(input_dict['Sleep_Duration'])
        if not (0 <= sleep <= 24):
            raise ValueError("Sleep Duration harus antara 0 dan 24 jam.")

    return True


# Import numpy locally to avoid top-level import issues
import numpy as np