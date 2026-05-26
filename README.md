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
