"""
Training Script untuk Model Decision Tree SPK Hipertensi
dengan Probability Calibration (Opsi B)
- Training 80% data
- GridSearchCV tuning
- Probability Calibration agar confidence realistis
- Visualisasi pohon keputusan
"""

import pandas as pd
import numpy as np
import json
import joblib
import matplotlib.pyplot as plt
from datetime import datetime

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# =========================
# KONFIGURASI
# =========================

DATASET_PATH = r"../SPK HYPERTENSION/hypertension_dataset.xlsx"
MODELS_DIR = "models"
TRAIN_SIZE = 0.8
RANDOM_STATE = 42

# Label mappings eksplisit (sesuai sheet Keterangan)
# Catatan: BP_History dan Exercise_Level dihapus dari fitur model.
# - BP_History dulunya importance 28% (tertinggi) — dihapus atas permintaan user.
# - Exercise_Level dulunya importance 0% (diabaikan model) — sekalian dibersihkan.
LABEL_MAPS = {
    'Family_History':  {'No': 0, 'Yes': 1},
    'Smoking_Status':  {'Non-Smoker': 0, 'Smoker': 1},
    'Has_Hypertension': {'No': 0, 'Yes': 1}
}

REVERSE_MAPS = {
    'Family_History': {0: 'No', 1: 'Yes'},
    'Smoking_Status':  {0: 'Non-Smoker', 1: 'Smoker'},
    'Has_Hypertension': {0: 'Tidak Hipertensi', 1: 'Hipertensi'}
}

# Urutan fitur yang dipakai model (harus sinkron dengan models/feature_names.json)
EXPECTED_FEATURES = [
    'Age', 'Salt_Intake', 'Stress_Score', 'Sleep_Duration',
    'BMI', 'Family_History', 'Smoking_Status',
]

# Kolom yang di-drop sebelum training
COLS_TO_DROP = ['Medication', 'BP_History', 'Exercise_Level']

# =========================
# 1. LOAD DATASET
# =========================

print("=" * 65)
print("  SPK HIPERTENSION - DECISION TREE + PROBABILITY CALIBRATION")
print("=" * 65)
print()

print("[1/8] Memuat dataset...")
df = pd.read_excel(DATASET_PATH, sheet_name="hypertension_dataset")
print(f"     Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"     Columns: {list(df.columns)}")

# =========================
# 2. PREPROCESSING
# =========================

print()
print("[2/8] Encoding data dengan label mapping eksplisit...")

df_encoded = df.copy()

for col, mapping in LABEL_MAPS.items():
    if col in df_encoded.columns:
        df_encoded[col] = df_encoded[col].map(mapping)
        print(f"     {col}: {mapping}")

# Drop kolom yang tidak dipakai model
existing_drops = [c for c in COLS_TO_DROP if c in df_encoded.columns]
if existing_drops:
    df_encoded = df_encoded.drop(columns=existing_drops)
    print(f"     [DROP] Kolom di-drop: {existing_drops}")

# =========================
# 3. SPLIT DATA
# =========================

print()
print("[3/8] Split feature dan target...")

TARGET = 'Has_Hypertension'
feature_cols = [col for col in df_encoded.columns if col != TARGET]
X = df_encoded[feature_cols]
y = df_encoded[TARGET]

# Assertion: pastikan urutan fitur sesuai kontrak
assert list(X.columns) == EXPECTED_FEATURES, (
    f"Feature order mismatch!\n"
    f"  Expected: {EXPECTED_FEATURES}\n"
    f"  Got:      {list(X.columns)}"
)

print(f"     Features ({len(feature_cols)}): {feature_cols}")
print(f"     Target: {TARGET}")

# =========================
# 4. TRAIN-TEST SPLIT
# =========================

print()
print("[4/8] Split train (80%) dan test (20%)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=TRAIN_SIZE,
    random_state=RANDOM_STATE, stratify=y
)

print(f"     Train: {X_train.shape[0]} samples")
print(f"     Test:  {X_test.shape[0]} samples")
print(f"     Tidak Hipertensi: {sum(y_train==0)} | Hipertensi: {sum(y_train==1)}")

# =========================
# 5. GRIDSEARCHCV TUNING
# =========================

print()
print("[5/8] Hyperparameter tuning GridSearchCV...")

param_grid = {
    'max_depth': [3, 4, 5, 6, 7, 8, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'criterion': ['entropy', 'gini']
}

grid_search = GridSearchCV(
    estimator=DecisionTreeClassifier(random_state=RANDOM_STATE),
    param_grid=param_grid,
    cv=5, scoring='accuracy', n_jobs=-1, verbose=0
)
grid_search.fit(X_train, y_train)

print("     Best params:")
for p, v in grid_search.best_params_.items():
    print(f"       {p}: {v}")

best_base_model = grid_search.best_estimator_

# =========================
# 6. PROBABILITY CALIBRATION (Isotonic Regression)
# =========================

print()
print("[6/8] Probability Calibration (Isotonic Regression, cv=5)...")
print("     -> Confidence akan lebih realistis (tidak selalu 100%)")

calibrated_model = CalibratedClassifierCV(
    estimator=DecisionTreeClassifier(
        **grid_search.best_params_,
        random_state=RANDOM_STATE
    ),
    method='isotonic',
    cv=5
)
calibrated_model.fit(X_train, y_train)
print("     Calibration selesai!")

# =========================
# 7. EVALUASI
# =========================

print()
print("[7/8] Evaluasi model...")

# Base model
base_pred = best_base_model.predict(X_test)
base_proba = best_base_model.predict_proba(X_test)

# Calibrated model
cal_pred = calibrated_model.predict(X_test)
cal_proba = calibrated_model.predict_proba(X_test)

# Metrik
base_acc  = accuracy_score(y_test, base_pred)
cal_acc   = accuracy_score(y_test, cal_pred)
cal_prec  = precision_score(y_test, cal_pred)
cal_rec   = recall_score(y_test, cal_pred)
cal_f1    = f1_score(y_test, cal_pred)

# Confidence distribution (calibrated)
cal_conf  = np.max(cal_proba, axis=1)

print()
print("=" * 65)
print("  HASIL EVALUASI")
print("=" * 65)
print()
print(f"  {'Metric':<15} {'Base Model':>12} {'Calibrated':>12}")
print(f"  {'-'*15} {'-'*12} {'-'*12}")
print(f"  {'Accuracy':<15} {base_acc:>12.4f} {cal_acc:>12.4f}")
print(f"  {'Precision':<15} {'':>12} {cal_prec:>12.4f}")
print(f"  {'Recall':<15} {'':>12} {cal_rec:>12.4f}")
print(f"  {'F1-Score':<15} {'':>12} {cal_f1:>12.4f}")
print()
print(f"  Confidence Distribution (Calibrated):")
print(f"    Min:    {cal_conf.min()*100:.1f}%")
print(f"    Mean:   {cal_conf.mean()*100:.1f}%")
print(f"    Max:    {cal_conf.max()*100:.1f}%")
print(f"    Std:    {cal_conf.std()*100:.1f}%")
print(f"    < 90%:  {sum(cal_conf < 0.9)} samples ({sum(cal_conf < 0.9)/len(cal_conf)*100:.1f}%)")

# Confusion Matrix
cm = confusion_matrix(y_test, cal_pred)
print()
print(f"  Confusion Matrix:")
print(f"                     Predicted")
print(f"                 {'Tidak Hipo':>12} {'Hipo':>12}")
print(f"  Actual Tidak     {cm[0][0]:>12} {cm[0][1]:>12}")
print(f"  Actual Hipo      {cm[1][0]:>12} {cm[1][1]:>12}")
print()
print(f"  Classification Report:")
print(classification_report(
    y_test, cal_pred,
    target_names=['Tidak Hipertensi', 'Hipertensi']
))

# Feature Importance (from base tree)
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': best_base_model.feature_importances_
}).sort_values('Importance', ascending=False)

print(f"  Feature Importance:")
for _, row in feature_importance.iterrows():
    bar_len = int(row['Importance'] * 30)
    bar = '#' * bar_len
    feat_name = row['Feature'][:20]
    imp_val = f"{row['Importance']:.4f}"
    print(f"    {feat_name:20s} {imp_val:>8s} |{bar}|")

# =========================
# 8. SIMPAN MODEL & ARTIFACTS
# =========================

print()
print("[8/8] Menyimpan model dan artifacts...")

# Save base tree (for visualization & animated walk)
joblib.dump(best_base_model, f"{MODELS_DIR}/base_tree.joblib")
print(f"     [SAVE] base_tree.joblib")

# Save calibrated model (for prediction with calibrated probability)
joblib.dump(calibrated_model, f"{MODELS_DIR}/model_calibrated.joblib")
print(f"     [SAVE] model_calibrated.joblib")

# Save feature names
with open(f"{MODELS_DIR}/feature_names.json", 'w') as f:
    json.dump(feature_cols, f, indent=2)
print(f"     [SAVE] feature_names.json")

# Save label mappings
with open(f"{MODELS_DIR}/label_mappings.json", 'w') as f:
    json.dump({'label_maps': LABEL_MAPS, 'reverse_maps': REVERSE_MAPS}, f, indent=2)
print(f"     [SAVE] label_mappings.json")

# Save training report
training_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(f"{MODELS_DIR}/training_report.txt", 'w') as f:
    f.write("=" * 65 + "\n")
    f.write("  TRAINING REPORT - SPK HIPERTENSION\n")
    f.write("  Decision Tree + Probability Calibration\n")
    f.write("=" * 65 + "\n\n")
    f.write(f"Training Date : {training_date}\n")
    f.write(f"Dataset       : {DATASET_PATH}\n")
    f.write(f"Total Samples : {len(X)}\n")
    f.write(f"Train Samples : {len(X_train)} ({TRAIN_SIZE*100:.0f}%)\n")
    f.write(f"Test Samples  : {len(X_test)} ({(1-TRAIN_SIZE)*100:.0f}%)\n\n")
    f.write("Best Parameters:\n")
    for p, v in grid_search.best_params_.items():
        f.write(f"  {p}: {v}\n")
    f.write("\nMetrics (Calibrated Model):\n")
    f.write(f"  Accuracy:  {cal_acc:.4f}\n")
    f.write(f"  Precision: {cal_prec:.4f}\n")
    f.write(f"  Recall:    {cal_rec:.4f}\n")
    f.write(f"  F1-Score:  {cal_f1:.4f}\n\n")
    f.write(f"Confidence Distribution:\n")
    f.write(f"  Min:  {cal_conf.min()*100:.1f}%\n")
    f.write(f"  Mean: {cal_conf.mean()*100:.1f}%\n")
    f.write(f"  Max:  {cal_conf.max()*100:.1f}%\n")
    f.write(f"  <90%: {sum(cal_conf < 0.9)} samples\n\n")
    f.write("Feature Importance:\n")
    for _, row in feature_importance.iterrows():
        f.write(f"  {row['Feature']}: {row['Importance']:.4f}\n")
print(f"     [SAVE] training_report.txt")

# ============================================================
# VISUALISASI POHON KEPUTUSAN (matplotlib plot_tree)
# ============================================================

print()
print("Membuat visualisasi pohon keputusan...")

# Visualisasi pohon keputusan UTuh
fig_tree, ax_tree = plt.subplots(figsize=(30, 18))
plot_tree(
    best_base_model,
    feature_names=feature_cols,
    class_names=['Tidak Hipertensi', 'Hipertensi'],
    filled=True,
    rounded=True,
    ax=ax_tree,
    fontsize=8,
    proportion=True,
    impurity=True
)
ax_tree.set_title(
    'Pohon Keputusan SPK Hipertensi\n(Decision Tree Classifier)',
    fontsize=20, fontweight='bold', pad=20
)
fig_tree.tight_layout()
fig_tree.savefig(f"{MODELS_DIR}/decision_tree_full.png", dpi=150, bbox_inches='tight')
print(f"     [SAVE] decision_tree_full.png")
plt.close(fig_tree)

# Visualisasi Feature Importance
fig_imp, ax_imp = plt.subplots(figsize=(10, 6))
imp_sorted = feature_importance.sort_values('Importance', ascending=True)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(imp_sorted)))
bars = ax_imp.barh(imp_sorted['Feature'], imp_sorted['Importance'], color=colors)
for bar, val in zip(bars, imp_sorted['Importance']):
    ax_imp.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=9)
ax_imp.set_xlabel('Importance Score', fontsize=12)
ax_imp.set_title('Feature Importance', fontsize=14, fontweight='bold')
ax_imp.set_xlim(0, imp_sorted['Importance'].max() * 1.18)
ax_imp.spines['top'].set_visible(False)
ax_imp.spines['right'].set_visible(False)
fig_imp.tight_layout()
fig_imp.savefig(f"{MODELS_DIR}/feature_importance.png", dpi=150, bbox_inches='tight')
print(f"     [SAVE] feature_importance.png")
plt.close(fig_imp)

print()
print("=" * 65)
print("  TRAINING + CALIBRATION SELESAI!")
print("=" * 65)
print()
print("  Jalankan aplikasi: python -m streamlit run spk_app.py")
print()
