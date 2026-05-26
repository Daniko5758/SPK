# SPK Hipertensi - Decision Tree Decision Support System

Sistem Pendukung Keputusan (SPK) untuk deteksi dini hipertensi menggunakan Decision Tree Classifier dengan Probability Calibration. Aplikasi ini dibangun dengan Streamlit dan menyediakan visualisasi pohon keputusan interaktif sekaligus explainable AI melalui decision path.

## Fitur Utama

- **Decision Tree + Probability Calibration** — Model klasifikasi dengan confidence score yang realistis
- **Visualisasi Decision Path** — Tampilkan step-by-step alur keputusan model untuk setiap input user
- **Feature Importance** — Pahami faktor-faktor paling berpengaruh terhadap prediksi hipertensi
- **Input Interaktif** — Form isian lengkap dengan validasi untuk 9 parameter klinis
- **Dashboard Model** — Laporan training, metrik evaluasi, dan confusion matrix

## Struktur Proyek

```
D:\SPK-HYPERTENSION-APP\
│
├── spk_app.py                 # Aplikasi utama Streamlit
├── train_model.py             # Script training model Decision Tree
├── requirements.txt          # Daftar dependency Python
│
├── models/                    # Artifact hasil training
│   ├── base_tree.joblib       # Decision Tree dasar (untuk visualisasi path)
│   ├── model_calibrated.joblib # Model dengan probability calibration
│   ├── feature_names.json     # Daftar nama fitur
│   ├── label_mappings.json    # Mapping label kategorik → numerik
│   ├── training_report.txt   # Laporan hasil training
│   ├── decision_tree_full.png # Visualisasi pohon keputusan lengkap
│   └── feature_importance.png # Grafik feature importance
│
└── utils/                     # Modul utility
    ├── __init__.py
    ├── encode.py              # Encoder/decoder label & validasi input
    ├── tree_walker.py         # Ekstrak decision path dari tree
    ├── visualizer.py          # Visualizer lama (deprecated)
    └── visualizer_v2.py       # Visualizer decision path (v4 - clean vertical tree)
```

## Persyaratan Sistem

- **Python** 3.9 atau lebih baru
- **Dataset** file `hypertension_dataset.xlsx` (sheet `hypertension_dataset`) di path yang disesuaikan di `train_model.py`

## Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd D--SPK-HYPERTENSION-APP
```

### 2. Setup Virtual Environment (Direkomendasikan)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependency

```bash
pip install -r requirements.txt
```

### 4. Setup Dataset

Pastikan file dataset tersedia. Edit `train_model.py` baris 29 untuk menyesuaikan path dataset:

```python
DATASET_PATH = r"D:\SPK HYPERTENSION\hypertension_dataset.xlsx"
```

Jika dataset ada di lokasi berbeda, ubah path tersebut.

### 5. Training Model (Opsional — Sudahinclude artifact pre-trained)

Jika belum ada artifact model di folder `models/`, atau ingin retrain dengan dataset terbaru:

```bash
python train_model.py
```

Script ini akan:
1. Load dan preprocess dataset dari Excel
2. Split data 80% train / 20% test
3. Hyperparameter tuning dengan GridSearchCV (5-fold CV)
4. Probability Calibration menggunakan Isotonic Regression
5. Evaluasi model (Accuracy, Precision, Recall, F1, Confusion Matrix)
6. Simpan semua artifact ke folder `models/`
7. Generate visualisasi pohon keputusan dan feature importance

## Menjalankan Aplikasi

```bash
python -m streamlit run spk_app.py
```

Atau:

```bash
streamlit run spk_app.py
```

Aplikasi akan terbuka otomatis di browser di `http://localhost:8501`.

## Fitur Aplikasi

### Halaman Utama — Form Input & Prediksi

| Fitur | Deskripsi |
|---|---|
| **Form Input Pasien** | 9 field input: Usia, Asupan Garam, Tingkat Stres, Riwayat Tekanan Darah, Durasi Tidur, BMI, Riwayat Keluarga, Aktivitas Fisik, Status Merokok |
| **Tombol Prediksi** | Jalankan prediksi dan tampilkan hasil |
| **Kartu Hasil** | Menampilkan label prediksi (Hipertensi / Tidak Hipertensi) beserta confidence score |
| **Probabilitas** | Breakdown probabilitas kedua kelas |
| **Decision Path** | Visualisasi vertical tree simpul-per-simpul dengan label YA/TIDAK |
| **Visualisasi Pohon** | Menampilkan pohon keputusan lengkap (matplotlib plot_tree) |
| **Feature Importance** | Grafik horizontal feature importance + top 3 faktor |
| **Detail Model** | JSON info model (max_depth, criterion, node count, dll) |
| **Laporan Training** | Expandable panel berisi laporan training lengkap |

### Fitur Decision Path

Visualisasi alur keputusan yang menunjukkan:
- Setiap simpul keputusan dengan nama fitur dan nilai input user
- Arah YA (kiri, hijau) atau TIDAK (kanan, merah) pada setiap percabangan
- Threshold pohon keputusan pada setiap simpul
- Simpul akhir (leaf) besar dengan hasil prediksi dan confidence score

## Dataset & Fitur

Dataset Excel (`hypertension_dataset.xlsx`) harus memiliki kolom:

| Kolom | Tipe | Deskripsi |
|---|---|---|
| `Age` | Numerik | Usia pasien (1–120 tahun) |
| `Salt_Intake` | Numerik | Asupan garam harian (gram, 0–25) |
| `Stress_Score` | Numerik | Skor stres (0–10) |
| `BP_History` | Kategorik | Riwayat tekanan darah: Normal, Prehypertension, Hypertension |
| `Sleep_Duration` | Numerik | Durasi tidur (jam, 0–24) |
| `BMI` | Numerik | Body Mass Index (10–80) |
| `Family_History` | Kategorik | Riwayat keluarga hipertensi: Yes, No |
| `Exercise_Level` | Kategorik | Aktivitas fisik: Low, Moderate, High |
| `Smoking_Status` | Kategorik | Status merokok: Smoker, Non-Smoker |
| `Has_Hypertension` | Target | Label: Yes (1), No (0) |

## Model & Metode

| Komponen | Detail |
|---|---|
| **Algoritma** | Decision Tree Classifier (`sklearn`) |
| **Hyperparameter Tuning** | GridSearchCV (max_depth, min_samples_split, min_samples_leaf, criterion) |
| **Probability Calibration** | Isotonic Regression via `CalibratedClassifierCV` (cv=5) |
| **Split Data** | 80% training / 20% testing |
| **Stratification** | Stratified split (proporsi kelas dijaga) |

---

## Detail Teknis

### 1. Cara Kerja Decision Tree

Decision Tree bekerja dengan membagi data secara rekursif berdasarkan fitur-fitur yang paling membedakan kelas target. Pada setiap node, pohon memilih **satu fitur** dan **satu threshold** yang memisahkan data se-optimal mungkin.

#### a. Kriteria Pemisahan (Split Criterion)

Dua metode yang diuji saat training via GridSearchCV:

**Gini Impurity** — Mengukur seberapa "kotor" suatu node (campuran kelas):
```
Gini(t) = 1 - Σ [p(i|t)]²

Contoh: Node dengan 70样本 Hipertensi, 30样本 Tidak Hipertensi
Gini = 1 - (0.7² + 0.3²) = 1 - (0.49 + 0.09) = 0.42

Semakin kecil Gini, semakin "murni" node tersebut
```

**Entropy** — Mengukur ketidakpastian/chaos di dalam node:
```
Entropy(t) = -Σ [p(i|t)] × log₂[p(i|t)]

Contoh: Node yang sama
Entropy = -(0.7 × log₂(0.7) + 0.3 × log₂(0.3))
         = -(0.7 × -0.515 + 0.3 × -1.737)
         = 0.361 + 0.521 = 0.882

Entropy = 0 → node murni (hanya satu kelas)
Entropy = 1 → node maximally impure (50/50)
```

#### b. Proses Splitting Rekursif

```
Root node (semua data)
│
├─ [Fitur A <= threshold?] YA → Branch kiri (subset data A)
│                               │
│                               ├─ [Fitur B <= threshold?] YA → ...
│                               └─ TIDAK → ...
│
└─ TIDAK → Branch kanan (subset data B)
            │
            ├─ YA → ...
            └─ TIDAK → ...
```

Pada setiap level, pohon menghitung **Information Gain** dari semua kemungkinan split:

```
Information Gain = Entropy(parent) - Weighted_Avg_Entropy(children)

                   |child_1|              |child_2|
Weighted_Avg = Entropy(child_1) × --------  + Entropy(child_2) × --------
                   |parent|               |parent|

Pohon memilih split dengan Information Gain tertinggi
```

#### c. Aturan Stopping

Pohon berhenti split ketika:
- `max_depth` tercapai
- `min_samples_split` tidak terpenuhi (minimum sample untuk memecah node)
- `min_samples_leaf` tidak terpenuhi (minimum sample di setiap leaf)
- Semua sample di node sudah satu kelas (pure)
- Tidak ada split yang meningkatkan impurity

#### d. Feature Importance

Feature importance dihitung berdasarkan **total pengurangan Gini/Entropy** yang dihasilkan oleh setiap fitur di seluruh node tree:
```
Importance(fitur) = Σ (pengurangan_impurity_node × jumlah_sample_node) / total_sample

Semakin besar nilainya, semakin penting fitur tersebut dalam klasifikasi
```

---

### 2. Probability Calibration — Kenapa Confidence Tidak Selalu 100%

Decision Tree yang belum di-calibrate cenderung memberikan **probability terlalu yakin (overconfident)**. Misalnya, suatu leaf node hanya berisi 3样本 Hipertensi dari 4 total sample, model akan melaporkan confidence 75% — padahal di data sebenarnya bisa jadi berbeda.

#### a. Overconfidence pada Raw Decision Tree

```
Leaf node punya:
  - 21样本 Hipertensi
  - 5样本 Tidak Hipertensi

Raw probability = 21/(21+5) = 80.8%

Tapi model TIDAK tahu bahwa dengan 26 sample, confidence 80.8% itu
mungkin overestimate karena tree terlalu spesifik ke training data
```

#### b. CalibratedClassifierCV dengan Isotonic Regression

Alur calibration:

```
1. Base Decision Tree melakukan prediksi pada data validation (cross-validation)
   → Didapat raw predicted probabilities dan actual labels

2. Isotonic Regression training:
   → Map raw probabilities ke calibrated probabilities
   → Bentuk monoton non-decreasing function yang menghubungkan
     raw prediction → true probability

3. Pada saat prediksi baru:
   → Decision Tree menghasilkan raw probability (misal 0.85)
   → Isotonic function memetakan 0.85 → calibrated value (misal 0.72)
   → Hasil akhir lebih realistis

   Cross-validation splitting (cv=5):
   ┌─────────────────────────────────────────────────┐
   │  Fold 1: Train 4/5 data, validate 1/5          │
   │  Fold 2: Train 4/5 data, validate 1/5          │
   │  Fold 3: Train 4/5 data, validate 1/5          │
   │  Fold 4: Train 4/5 data, validate 1/5          │
   │  Fold 5: Train 4/5 data, validate 1/5          │
   └─────────────────────────────────────────────────┘
   → Setiap sample pernah jadi validation set
   → Semua hasil digabungkan untuk bangun isotonic curve
```

**Mengapa Isotonic Regression?** Non-parametric, tidak mengasumsikan bentuk kurva tertentu, cukup fleksibel untuk menyesuaikan probabilitas raw ke probabilitas actual.

---

### 3. Proses Encoding Data

Encoding terjadi di **dua tahap**: saat training (`train_model.py`) dan saat inference (`spk_app.py` + `utils/encode.py`).

#### a. Encoding di Training (`train_model.py`)

Dataset awal (string/label) → dikonversi ke angka sebelum training:

```python
LABEL_MAPS = {
    'BP_History':     {'Normal': 1, 'Prehypertension': 2, 'Hypertension': 3},
    'Family_History': {'No': 0, 'Yes': 1},
    'Exercise_Level': {'Low': 1, 'Moderate': 2, 'High': 3},
    'Smoking_Status': {'Non-Smoker': 0, 'Smoker': 1},
    'Has_Hypertension': {'No': 0, 'Yes': 1}   # target column
}

# Proses: df['BP_History'].map({'Normal': 1, 'Prehypertension': 2, ...})
```

Fitur numerik (`Age`, `Salt_Intake`, `BMI`, `Stress_Score`, `Sleep_Duration`) TIDAK di-encode karena sudah berupa angka — langsung dipakai apa adanya.

**Urutan Feature Names** disimpan ke `feature_names.json` untuk memastikan urutan input saat inference konsisten dengan urutan saat training. Urutan ini penting karena model sklearn mengakses kolom berdasarkan index, bukan nama.

#### b. Encoding di Inference (`utils/encode.py`)

Ketika user mengisi form di Streamlit, input berupa angka/bukan string semua kecuali yang kategorik. Fungsi `encode_input()` melakukan:

```python
def encode_input(input_dict):
    label_maps, _ = _load_mappings()  # Load dari label_mappings.json
    encoded = {}

    for feature, value in input_dict.items():
        if feature in label_maps:
            # Kategorik: string → angka (mapping)
            #   'Normal' → 1, 'Prehypertension' → 2, dst.
            encoded[feature] = label_maps[feature][value]
        else:
            # Numerik: langsung cast ke float
            #   Age=45 → 45.0, BMI=23.5 → 23.5
            encoded[feature] = float(value)

    return encoded
```

Langkah akhir: konversi ke list berdasarkan urutan `feature_names`:

```python
def encode_to_model_input(input_dict, feature_names):
    encoded = encode_input(input_dict)
    return [encoded[feat] for feat in feature_names]
    # Hasil: [45.0, 8.0, 5.0, 1, 7.0, 25.0, 0, 1, 1]
    #         Age  Salt  Stress  BP  Sleep  BMI  Family Exer  Smoke
```

#### c. Reverse Mapping (Decode)

Hasil prediksi (angka) dikembalikan ke label readable:

```python
REVERSE_MAPS = {
    'Has_Hypertension': {0: 'Tidak Hipertensi', 1: 'Hipertensi'}
}
pred_label = reverse_maps['Has_Hypertension'].get(predicted_class, ...)
```

---

### 4. Alur Prediksi Lengkap

```
USER INPUT (Streamlit Form)
│
├─ BP_History: "Normal"          ← string
├─ Age: 52                       ← integer
├─ Salt_Intake: 12.5             ← float
└─ ... (9 fitur total)
│
▼  [encode_to_model_input()]
│
ENCODE → [52.0, 12.5, 5.0, 1, 7.0, 25.0, 0, 1, 1]
         │       │     │   │    │    │    │  │  │
         Age    Salt  Str BP   Slp  BMI  Fam Exr Smo
│
▼  [np.array().reshape(1, -1)] → shape (1, 9)
│
├─ ① base_tree.decision_path(X)  → Extract decision path (untuk visualisasi)
│   Setiap node: fitur apa, threshold apa, nilai input masuk branch mana
│
├─ ② calibrated_model.predict(X)  → Prediksi kelas (0 atau 1)
│   Hipertensi / Tidak Hipertensi
│
└─ ③ calibrated_model.predict_proba(X)  → [prob_0, prob_1]
    Probabilitas kedua kelas
    Confidence = max(prob_0, prob_1)
    │
    ▼
    reverse_maps['Has_Hypertension'] → Label string
    │
    ▼
    DISPLAY: Kartu hasil + Metric probabilitas + Decision Path (leaf)
```

---

### 5. Teknologi & Library

| Library | Versi Minimal | Fungsi |
|---|---|---|
| **streamlit** `st` | ≥1.28 | Web framework — membangun UI interaktif (form, metric, chart, image display). Tanpa streamlit, aplikasi ini CLI-only. |
| **scikit-learn** `sklearn` | ≥1.3 | DecisionTreeClassifier (base model), CalibratedClassifierCV (calibration), GridSearchCV (hyperparameter tuning), train_test_split, metrics |
| **pandas** `pd` | ≥2.0 | Load & manipulasi dataset Excel, DataFrame operations |
| **openpyxl** | ≥3.1 | Engine untuk membaca file `.xlsx` oleh pandas |
| **joblib** | ≥1.3 | Serialisasi model (`.joblib`) — load/dump objek Python besar (model trained) ke disk. Lebih efisien daripada pickle untuk numpy arrays. |
| **numpy** `np` | ≥1.24 | Komputasi array numerik, reshape input, argmax |
| **matplotlib** `plt` | ≥3.7 | Visualisasi pohon keputusan (`plot_tree`), feature importance bar chart, decision path rendering via `Figure`, `FancyBboxPatch`, `annotate` |
| **PIL (Pillow)** | — | Membaca image `decision_tree_full.png` dari disk untuk ditampilkan di Streamlit |

**Mengapa joblib untuk model, bukan pickle?**
- joblib内部 pakai numpy serialization yang lebih efisien untuk array besar
- Cross-platform compatible
- Compression support untuk file besar
-sklearn sendiri menggunakan joblib sebagai default untuk `joblib.dump/load`

---

### 6. Feature Importance & Interpretasi

Feature importance dihitung berdasarkan kontribusi setiap fitur dalam mengurangi impurity (Gini/Entropy) di seluruh node tree:

```
Importance(fitur) = Σ (ΔGini × n_sample) / Σ (ΔGini × n_sample) semua fitur

Contoh hasil (model terlatih):
  Age              0.312  ← Paling berpengaruh
  BP_History       0.287
  Salt_Intake      0.198
  BMI              0.112
  Stress_Score     0.047
  Sleep_Duration   0.028
  Family_History    0.009
  Exercise_Level   0.005
  Smoking_Status   0.002
```

**Catatan**: Nilai importance bersifat relatif antar fitur pada model yang sama. Tidak bisa dibanding-bandingkan antar model yang berbeda.

---

### 7. Catatan Penting untuk User

**Tentang Probabilitas (Confidence)**

- Confidence yang ditampilkan menggunakan **probability dari model yang sudah di-calibrate** (Isotonic Regression), bukan probability raw dari Decision Tree
- Calibration membuat confidence lebih realistis — tidak lagi 100% untuk hampir semua kasus
- Confidence bukan "proporsi akurasi", melainkan **estimasi seberapa yakin model terhadap prediksinya berdasarkan distribusi di leaf node yang sesuai**

**Tentang Decision Path**

- Decision Path menunjukkan **rute spesifik** yang diambil oleh input user melalui pohon keputusan
- Path berbeda untuk setiap kombinasi input
- Threshold di setiap node ditentukan saat training berdasarkan dataset
- `tree_walker.py` menggunakan `base_tree` (bukan calibrated model) karena hanya base tree yang menyimpan struktur node dan threshold asli

**Tentang GridSearchCV**

- Model terbaik dipilih berdasarkan **5-fold cross-validation accuracy**
- Parameter yang di-tune: `max_depth`, `min_samples_split`, `min_samples_leaf`, `criterion` (gini/entropy)
- Best params disimpan di `training_report.txt`

**Keterbatasan Model**

- Decision Tree bersifat deterministik — input yang sama akan selalu menghasilkan output yang sama
- Model tidak memperhitungkan interaksi non-linear antar fitur di luar yang bisa di-capture oleh tree splits
- Confidence rendah (misal <60%) menandakan input berada di region ambiguous — perlu konsultasi ahli

---

## Dependency

```
streamlit>=1.28
scikit-learn>=1.3
pandas>=2.0
openpyxl>=3.1
plotly>=5.18
joblib>=1.3
numpy>=1.24
matplotlib>=3.7
```

## Troubleshooting

```
streamlit>=1.28
scikit-learn>=1.3
pandas>=2.0
openpyxl>=3.1
plotly>=5.18
joblib>=1.3
numpy>=1.24
matplotlib>=3.7
```

## Troubleshooting

### Error: Model tidak ditemukan

```bash
python train_model.py
```

Pastikan path dataset di `train_model.py` sudah benar.

### Error: Dataset file not found

Pastikan file `hypertension_dataset.xlsx` ada di path yang ditentukan di `train_model.py` baris 29.

### matplotlib Font Warning

Jika muncul warning tentang font, bisa diabaikan — tidak mempengaruhi fungsionalitas aplikasi.

## Lisensi

Proyek ini merupakan implementasi SPK (Sistem Pendukung Keputusan) untuk deteksi hipertensi berbasis machine learning.
