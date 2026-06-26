<div align="center">

# ⛏️ PRATYAKSA

### AIoT Predictive + Prescriptive Maintenance for Heavy Mining Equipment

**Edge-Cloud AI system** — from sensor telemetry to real-time prediction, SHAP explainability, digital twin cross-check, and automated work orders. Built for **zero unplanned breakdowns**.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square)
![XGBoost](https://img.shields.io/badge/XGBoost-3.2-orange?style=flat-square)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-FF6F00?style=flat-square)
![Keras](https://img.shields.io/badge/Keras-3.14-D00000?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-latest-2DC897?style=flat-square)
![Docker](https://img.shields.io/badge/docker-compose-blue?style=flat-square)
![Edge](https://img.shields.io/badge/edge-RPi%20Zero%202W-c51a4a?style=flat-square)

</div>

---

## 📋 Daftar Isi

- [Masalah & Solusi](#-masalah--solusi)
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Fitur Utama](#-fitur-utama)
- [Model Machine Learning](#-model-machine-learning)
- [Tech Stack](#-tech-stack)
- [Cara Memulai (Quick Start)](#-cara-memulai-quick-start)
- [Daftar Service](#-daftar-service)
- [Daftar Endpoint API](#-daftar-endpoint-api)
- [Environment Variables](#-environment-variables)
- [Testing](#-testing)
- [Struktur Proyek](#-struktur-proyek)
- [Data Pipeline (Notebooks)](#-data-pipeline-notebooks)
- [Roadmap](#-roadmap)
- [Cara Berkontribusi](#-cara-berkontribusi)
- [Lisensi](#-lisensi)
- [Kontak](#-kontak)

---

## 🧩 Masalah & Solusi

### Masalah

Alat berat tambang (haul truck, excavator, bulldozer, wheel loader) menghadapi tiga tantangan utama:

| Masalah | Dampak |
|---------|--------|
| 🔧 **Kerusakan mendadak (*unplanned breakdown*)** — tidak ada peringatan dini sebelum komponen kritis gagal | Downtime produksi hingga 12+ jam, biaya perbaikan darurat 2–5× lebih mahal |
| 📊 **Keputusan maintenance reaktif** — perbaikan hanya dilakukan setelah kerusakan terjadi | Utilisasi alat rendah (<75%), biaya maintenance tinggi, umur pakai komponen tidak optimal |
| 🧠 **Keahlian terbatas** — teknisi ahli terpusat di site, tidak bisa memonitor 30+ unit sekaligus | Eskalasi masalah lambat, keputusan tidak konsisten antar shift |

### Solusi

**PRATYAKSA** menghadirkan sistem prediktif end-to-end yang terintegrasi dari sensor hingga tindakan:

```
┌──────────────────────────────────────────────────────────────────────┐
│  📡 LAPISAN 1: Edge Device (Raspberry Pi Zero 2W)                    │
│     Baca sensor (ADXL345, MAX6675, Pressure Transducer)             │
│     Inferensi ONNX Runtime (XGBoost → risk_score)                   │
│     Digital Twin (physics-based RUL estimation)                     │
│     Offline buffer SQLite (72 jam) → MQTT publish                   │
├──────────────────────────────────────────────────────────────────────┤
│  ☁️ LAPISAN 2: Cloud Backend (FastAPI + Redis Streams)               │
│     MQTT → Redis Bridge → Inference API                             │
│     Dual-model: XGBoost classifier + LSTM MoE regressor             │
│     SHAP explainability, drift detection, flatline detection        │
├──────────────────────────────────────────────────────────────────────┤
│  🏭 LAPISAN 3: MLOps & Monitoring                                    │
│     TimescaleDB (sensor + prediction history)                       │
│     MLflow experiment tracking, Airflow retrain pipeline            │
│     Grafana dashboard, Telegram alert bot, Prometheus metrics       │
├──────────────────────────────────────────────────────────────────────┤
│  🔧 LAPISAN 4: Prescriptive Action                                   │
│     Work order recommendation engine (spare parts + cost)           │
│     Automated Telegram alerts for CRITICAL conditions               │
└──────────────────────────────────────────────────────────────────────┘
```

### Alur Data Sistem

```
Edge Device (RPi) ──MQTT──► Mosquitto ──► Bridge ──► Redis Streams
                                                           │
                                                           ▼
                                                    FastAPI Inference
                                                    ├─ XGBoost (3-class)
                                                    ├─ LSTM MoE (RUL)
                                                    ├─ Digital Twin
                                                    ├─ Drift Detection
                                                    └─ Risk Resolution
                                                           │
                                              ┌────────────┼────────────┐
                                              ▼            ▼            ▼
                                        TimescaleDB    Redis Cache   Telegram Bot
                                     (sensor + pred)  (result:{id})  (alerts)
                                              │
                                        Grafana / Prometheus
```

---

## 🏛️ Arsitektur Sistem

```mermaid
flowchart LR
  Edge["Edge (RPi Zero 2W)
  ONNX Runtime + Nextion HMI"] -->|MQTT| Mosquitto
  Sim["Simulator"] -->|MQTT| Mosquitto
  Mosquitto --> Bridge["MQTT→Redis Bridge"]
  Bridge --> Redis[(Redis Streams)]
  Redis --> API["Inference API
  FastAPI + XGBoost + LSTM"]
  API --> PG[(PostgreSQL
  TimescaleDB)]
  API --> Bot["Telegram Bot"]
```

### Port yang Digunakan

| Service | Host Port | Container Port |
|---------|:---------:|:--------------:|
| FastAPI Inference API | **6000** | 8000 |
| Grafana Dashboard | **6001** | 3000 |
| MLflow Tracking | **6050** | 5000 |
| Airflow Webserver | **6080** | 8080 |
| Prometheus | **6090** | 9090 |
| Mosquitto MQTT | **6883** | 1883 |
| Mosquitto WebSocket | **6884** | 9001 |
| Redis | **6379** | 6379 |
| PostgreSQL (TimescaleDB) | **5432** | 5432 |

---

## ✨ Fitur Utama

### 1. 🔮 Predictive Maintenance (Dual-Model Ensemble)
- **XGBoost Classifier** (96.85% accuracy) — 3-class anomaly detection: NORMAL, WARNING, CRITICAL
- **LSTM MoE (Mixture of Experts)** — Hierarchical RUL estimation (system → component → part) with Monte Carlo Dropout for uncertainty quantification
- **Risk Resolution** — Jika XGBoost dan LSTM berbeda, ambil kelas terburuk (max of both)
- **37 fitur sensor** meliputi: telemetri mesin (12), kondisi fisik/fluida (10), konteks lingkungan (8), maintenance logs (2), + dropout flags (5)

### 2. 🔧 Prescriptive Maintenance (P4)
- Risk score > 0.7 → otomatis rekomendasi *Create Work Order*
- Integrasi database spare parts untuk estimasi biaya
- Rekomendasi komponen spesifik (hydraulic pump, brake pad, bearing, seal, dll)

### 3. 🧠 Digital Twin — Physics-Based Cross-Check
- **Brake RUL** — berdasarkan payload × grade × distance vs cumulative work (max 800h)
- **Bearing RUL** — threshold-based pada vibration_z_g (5g → 0h, 3.2g → 12h, 1.4g → 72h)
- **Hydraulic RUL** — linear degradation dari nominal pressure (280 bar), 0h saat drop >80 bar
- Berjalan di **Edge** (ONNX) maupun **Cloud** (FastAPI) sebagai verifikasi silang

### 4. 📊 SHAP Explainability
- `GET /explain/{prediction_id}` — waterfall plot (base64 PNG) menampilkan fitur dengan kontribusi tertinggi
- **Top features**: `acoustic_emission_db` (45.4%), `vibration_z_g` (23.5%)
- TreeExplainer untuk model XGBoost

### 5. 🚨 Drift Detection & Sensor Quality Assurance
- **Real-time Z-score drift detection** — flag fitur dengan |z| > 3.0
- **Batch KS-test drift detection** — dijalankan daily via Airflow DAG
- **Flatline detection** — std < 1e-6 dalam 10 readings → dropout flags
- **Connectivity gap detection** — gap > 120 menit tercatat

### 6. 📈 Fleet Monitoring
- `/fleet` endpoint — ringkasan semua unit aktif, diurutkan berdasarkan risk
- `active_assets` set di Redis — melacak unit yang sedang aktif
- Grafana dashboard dengan hourly aggregates dari continuous aggregate TimescaleDB

### 7. 🔄 MLOps — End-to-End Pipeline
- **MLflow** tracking untuk experiments (XGBoost + LSTM)
- **Airflow** retrain pipeline (mingguan, Minggu tengah malam) — extract → retrain → hot-reload
- **Zero-downtime hot-reload** model via `POST /reload-models`
- **Model gate checks**: MAE_critical, bias_critical

### 8. 🤖 Telegram Alerting
- **Critical alerts** otomatis terkirim ke Telegram (unit info, SHAP analysis, spare parts, CMMS link)
- **Fleet status command** — `/status` untuk ringkasan fleet (critical/warning/normal)

---

## 🤖 Model Machine Learning

### XGBoost Classifier

| Metrik | Nilai |
|--------|-------|
| Akurasi | **96.85%** |
| Recall CRITICAL | **93.94%** |
| Silent Misses | **0** |
| Threshold CRITICAL | 0.29 (F2-optimized) |
| Objective | `multi:softprob` (3 kelas) |
| Parameters | n=2000, max_depth=6, lr=0.05, subsample=0.8, colsample=0.8 |

**Top Features** (gain): `acoustic_emission_db` (45.4%), `vibration_z_g` (23.5%), dropout flags.

### LSTM MoE — PRATYAKSAExpert

| Komponen | Detail |
|----------|--------|
| **Arsitektur** | 3-layer LSTM (128→64→32) + Dense(16) + MC Dropout(0.1) |
| **Input** | 20 timesteps × 37 features (sliding window) |
| **Output** | RUL_hours + 7 hierarchical targets (hydraulic, brake, steering) |
| **MC Dropout** | 20 forward passes → mean + std (uncertainty) |
| **Custom Loss** | `asymmetric_loss` — overprediction penalty 20× saat RUL < 100h |

**Per-Equipment Performance:**

| Tipe Alat | MAE Test | MAE Critical |
|-----------|:--------:|:------------:|
| Bulldozer D155 | 123h | 11.5h |
| Haul Truck HD785 | 85.4h | 9.3h |
| Excavator PC2000 | 67.2h | 10.4h |
| Wheel Loader WA600 | 87.6h | 9.7h |

### Edge Model (ONNX Runtime)

XGBoost diekspor ke format ONNX (340 KB) untuk inferensi di Raspberry Pi Zero 2W.

### Digital Twin — Physics Models

| Komponen | Metode | Max RUL |
|----------|--------|:-------:|
| Brake | Payload × grade × distance vs cumulative work | 800h |
| Bearing | Vibration threshold (5g → 0h) | 500h |
| Hydraulic | Linear degradation from 280 bar nominal | 500h |

---

## 🛠️ Tech Stack

| Kategori | Teknologi |
|----------|-----------|
| **Bahasa** | Python 3.11 |
| **API Framework** | FastAPI 0.136, Uvicorn 0.49 |
| **ML/DL** | XGBoost 3.2, Keras 3.14 + TensorFlow 2.21, scikit-learn 1.8 |
| **Edge Inference** | ONNX Runtime (model ONNX dari XGBoost) |
| **Explainability** | SHAP 0.51, Matplotlib |
| **Database** | PostgreSQL 16 + TimescaleDB (hypertable + compression) |
| **Cache & Stream** | Redis 8 (streams, pub/sub, cache, TTL) |
| **Edge Buffer** | SQLite (offline buffer 72 jam) |
| **Async DB** | SQLAlchemy 2.0 (async), asyncpg |
| **MQTT** | paho-mqtt, Mosquitto broker |
| **Monitoring** | Prometheus, Grafana, prometheus-fastapi-instrumentator |
| **MLOps** | MLflow 3.13, Apache Airflow 2.9 |
| **Alerting** | Telegram Bot API (httpx) |
| **Data Processing** | Pandas, NumPy, PyArrow, FastParquet |
| **Orkestrasi** | Docker Compose (non-root containers, healthchecks) |
| **Edge Hardware** | Raspberry Pi Zero 2W, Nextion HMI, ADXL345, MAX6675 |

---

## 🚀 Cara Memulai (Quick Start)

### Prasyarat

- Docker & Docker Compose terinstal
- Git
- Port 6000, 6001, 6050, 6080, 6090, 6379, 5432, 6883, 6884 tersedia

### 1. Clone & Konfigurasi

```bash
git clone <repository-url>
cd pratyaksa

cp .env.example .env
# Edit .env — set:
#   POSTGRES_PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PRATYAKSA_API_KEYS
```

### 2. Jalankan Stack (Development)

```bash
docker compose --profile dev up -d
```

Tunggu beberapa saat hingga semua container siap. Cek status:

```bash
docker compose ps
```

### 3. Verifikasi

```bash
# Health check
curl http://localhost:6000/health

# Kirim sample prediction
curl -X POST http://localhost:6000/predict \
  -H "X-API-Key: dev-key-pratyaksa" \
  -H "Content-Type: application/json" \
  -d '{"asset_id":"test-001","equipment_type":"haul_truck","features":[1.0]*37}'
```

### 4. Akses Layanan

| Layanan | URL | Keterangan |
|---------|-----|------------|
| **FastAPI Docs** | http://localhost:6000/docs | Swagger UI |
| **Grafana** | http://localhost:6001 | admin / pratyaksa2026 |
| **MLflow** | http://localhost:6050 | Experiment tracking |
| **Airflow** | http://localhost:6080 | DAG monitoring |
| **Prometheus** | http://localhost:6090 | Metrics explorer |

### 5. Jalankan Simulator Data

```bash
# Sudah berjalan otomatis jika menggunakan --profile dev
# Untuk menjalankan manual:
docker compose exec simulator python stream_simulator.py
```

### 6. Hentikan Stack

```bash
docker compose down
```

---

## 📡 Daftar Service

| Service | Port | Deskripsi |
|---------|:----:|-----------|
| **pratyaksa-redis** | 6379 | Redis 8 — Streams, pub/sub, cache result (TTL 1h), active assets set |
| **pratyaksa-postgres** | 5432 | TimescaleDB 16 — Hypertable sensor + prediction (compress 30d, retain 2y) |
| **pratyaksa-api** | 6000 | FastAPI — Inference engine (predict, explain, workorder, fleet, health) |
| **pratyaksa-bot** | — | Telegram bot — Alert listener + command handler (/start, /status) |
| **pratyaksa-mlflow** | 6050 | MLflow 3.13 — Experiment tracking (Postgres backend) |
| **pratyaksa-prometheus** | 6090 | Prometheus 2.51 — Metrics scraping (30d retention) |
| **pratyaksa-grafana** | 6001 | Grafana 10.4 — Fleet dashboard + unified alerting |
| **pratyaksa-simulator** | — | Stream simulator (dev profile) — replay parquet data |
| **pratyaksa-airflow-scheduler** | — | Airflow scheduler — retrain + drift + quality DAGs |
| **pratyaksa-airflow-web** | 6080 | Airflow webserver — DAG UI |
| **mosquitto** | 6883 | MQTT broker — edge data ingestion |
| **bridge** | — | MQTT→Redis bridge — edge/data → stream:sensors:{equipment_type} |

---

## 📡 Daftar Endpoint API

| Method | Path | Auth | Deskripsi | Contoh Respons |
|--------|------|:----:|-----------|----------------|
| `GET` | `/health` | ✗ | Health check (Redis, Postgres, models) | `{"status":"healthy","redis":"ok","postgres":"connected","model_xgb":"loaded"}` |
| `GET` | `/metrics` | ✗ | Prometheus metrics | `http_requests_total 42` |
| `POST` | `/predict` | API Key | Prediksi tunggal — risk, RUL, twin, drift | `{"asset_id":"test-001","risk_score":0.85,"xgb_class":2,"lstm_rul_hours":47.2,...}` |
| `GET` | `/explain/{prediction_id}` | API Key | SHAP waterfall plot (base64 PNG) | `{"prediction_id":"...","waterfall_plot":"iVBORw0KGgo..."}` |
| `POST` | `/workorder` | API Key | Rekomendasi work order preskriptif | `{"recommendation":"Create Work Order","parts":[...],"total_cost":12500000}` |
| `GET` | `/result/{asset_id}` | ✗ | Latest cached prediction | `{"risk_score":0.85,"xgb_class":2,"lstm_rul_hours":47.2}` |
| `GET` | `/fleet` | ✗ | Fleet status agregat | `{"total_units":5,"critical":1,"warning":2,"normal":2}` |
| `POST` | `/reload-models` | API Key | Hot-reload model tanpa downtime | `{"status":"ok","reloaded":["xgb","lstm","scaler","metadata"]}` |

---

## 🔐 Environment Variables

| Variable | Required | Default | Deskripsi |
|----------|:--------:|:-------:|-----------|
| `POSTGRES_PASSWORD` | ✅ | — | Password PostgreSQL |
| `PRATYAKSA_API_KEYS` | ✅ | — | Comma-separated API keys untuk endpoint |
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Token bot Telegram |
| `TELEGRAM_CHAT_ID` | ✅ | — | Chat ID Telegram untuk alert |
| `ENV` | ❌ | `development` | Mode environment (`development` / `production`) |
| `GRAFANA_PASSWORD` | ❌ | `pratyaksa2026` | Password admin Grafana |
| `REDIS_URL` | ❌ | `redis://redis:6379` | Redis connection URL |
| `DATABASE_URL` | ❌ | `postgresql://pratyaksa:${POSTGRES_PASSWORD}@postgres:5432/pratyaksa` | PostgreSQL connection URL |

---

## 🧪 Testing

### Unit Tests

```bash
# Environment must be development
ENV=development python test_core.py -v

# Load test
python test_load.py
```

**Lingkup test:**
- ✅ Risk resolution (XGBoost vs LSTM conflict)
- ✅ Hierarchy enforcement (part ≤ component ≤ system)
- ✅ Digital Twin physics models (brake, bearing, hydraulic)
- ✅ Drift detection (Z-score)
- ✅ Dropout flag detection (flatline, NaN)
- ✅ Health endpoint
- ✅ Integration test (stream → Redis → API → predict)

### Integration Test

```bash
curl -X POST http://localhost:6000/predict \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"asset_id":"test-001","equipment_type":"haul_truck","features":[1.0]*37}'
```

---

## 📁 Struktur Proyek

```
pratyaksa/
├── docker-compose.yml               # Orkestrasi 12 service
├── .env.example                     # Template environment variables
├── schema_config.json               # Definisi 37 fitur sensor (4 grup)
├── bridge.py                        # MQTT → Redis Stream bridge
├── export_onnx.py                   # Export XGBoost → ONNX untuk edge
├── test_core.py                     # Unit test suite
├── test_load.py                     # Load test
├── requirements-dev.txt             # Dependencies development (notebook, ML)
├── artifacts/                       # Model artifacts
│   ├── artifact_xgb_model.json      # XGBoost classifier
│   ├── artifact_xgb_model.onnx      # ONNX export (340 KB)
│   ├── artifact_scaler.pkl          # StandardScaler (37 fitur)
│   ├── artifact_metadata.json       # Threshold, feature names, perf metrics
│   └── experts/                     # LSTM MoE per equipment type
│       ├── expert_bulldozer.keras
│       ├── expert_haul_truck.keras
│       ├── expert_excavator.keras
│       └── expert_wheel_loader.keras
├── api/                             # ☁️ Cloud Backend
│   ├── app.py                       # FastAPI — 8 endpoints (1015 line)
│   ├── prescriptive.py              # Recommendation engine (spare parts)
│   └── requirements.txt             # Dependencies API
├── edge/                            # 📡 Edge Device (RPi Zero 2W)
│   ├── main.py                      # Main loop: sensor → inference → MQTT
│   ├── inference.py                 # ONNX Runtime orchestrator
│   ├── preprocessor.py              # StandardScaler transform
│   ├── risk_resolver.py             # Risk + Digital Twin resolver
│   ├── digital_twin.py              # Physics model (brake/bearing/hydraulic)
│   ├── buffer.py                    # SQLite offline buffer (72 jam TTL)
│   ├── mqtt_edge.py                 # MQTT client dengan offline buffer
│   ├── nextion.py                   # Nextion HMI serial driver
│   └── drivers/                     # Hardware drivers
│       ├── adxl345.py               # Accelerometer (3-axis)
│       ├── max6675.py               # Thermocouple
│       └── pressure_transducer.py   # Pressure transducer
├── bot/                             # 🤖 Telegram Alerting
│   ├── bot.py                       # Main bot (alert listener + commands)
│   └── bot_simulator.py             # FastAPI simulator (testing tanpa Redis)
├── simulator/                       # 🔄 Data Simulator
│   └── stream_simulator.py          # Async replay parquet → Redis Streams
├── airflow/dags/                    # 🏭 MLOps Pipeline
│   ├── retrain_pipeline.py          # Weekly retrain (XGBoost + LSTM)
│   ├── daily_data_quality.py        # Daily null check
│   └── daily_drift_detection.py     # Daily KS-test drift detection
├── monitoring/                      # 📊 Monitoring
│   └── prometheus.yml               # Prometheus scrape config
├── database/                        # 🗄️ Database Schema
│   └── schema.sql                   # TimescaleDB hypertables + views
├── notebooks/                       # 📓 Jupyter Notebooks
│   ├── data_pipeline.ipynb          # Synthetic fleet data generation
│   └── model_pipeline.ipynb         # Model training (XGBoost + LSTM)
├── docker-container/                # Docker support files
└── data/                            # Data directory
```

---

## 📓 Data Pipeline (Notebooks)

### `notebooks/data_pipeline.ipynb`
Pipeline generate data sintetis untuk 30 unit alat berat (12 haul truck, 6 excavator, 6 bulldozer, 6 wheel loader) dengan ~148k baris data per jam. Memuat:
- Physics-compliant sensor degradation (degradation_factor = exp(-5 × RUL / max_RUL))
- Hierarchy constraints (part ≤ component ≤ system)
- Sensor quality validation (flatline, gap, NaN imputation)
- LSTM sequence construction (window=24, stepped per hour)
- Ekspor 5-unit pilot subset untuk testing

### `notebooks/model_pipeline.ipynb`
Pipeline training model (XGBoost + LSTM MoE):
- Load & split data, StandardScaler fitting
- XGBoost training dengan threshold tuning (F2-optimized)
- SHAP analysis (feature importance, waterfall plot)
- PRATYAKSAExpert LSTM training per equipment type dengan MLflow logging

---

## 🗺️ Roadmap

- [x] **Fase 1** — Sensor data pipeline & synthetic data generation
- [x] **Fase 2** — Dual-model development (XGBoost + LSTM MoE)
- [x] **Fase 3** — Cloud API (FastAPI + Redis Streams + TimescaleDB)
- [x] **Fase 4** — Edge device (ONNX Runtime + RPi Zero 2W)
- [x] **Fase 5** — Digital Twin physics models
- [x] **Fase 6** — MLOps (MLflow tracking + Airflow retrain + hot-reload)
- [x] **Fase 7** — Monitoring (Prometheus + Grafana + Telegram bot)
- [x] **Fase 8** — SHAP explainability + Prescriptive engine
- [ ] **Fase 9** — CMMS integration (SAP / Oracle)
- [ ] **Fase 10** — Multi-site deployment (regional edge gateway)
- [ ] **Fase 11** — Real drone-based thermal inspection integration
- [ ] **Fase 12** — On-device continual learning (Federated Learning)

---

## 🤝 Cara Berkontribusi

Kami menyambut kontribusi! Berikut panduannya:

1. **Fork** repository ini
2. Buat branch fitur: `git checkout -b fitur-keren-anda`
3. **Commit** perubahan: `git commit -m 'Menambahkan fitur keren'`
4. **Push** ke branch: `git push origin fitur-keren-anda`
5. Buat **Pull Request**

### Pedoman

- Semua kode baru harus disertai **unit test**
- Gunakan **Bahasa Inggris** untuk kode dan komentar teknis
- Ikuti **code style** yang sudah ada (lihat file yang sudah ada sebagai referensi)
- Jika menemukan bug, buka **Issue** terlebih dahulu

---

## 📄 Lisensi

Proyek ini dikembangkan untuk **PT. Kideco Jaya Agung** — Hak cipta dilindungi undang-undang.

```
PRATYAKSA — AIoT Predictive + Prescriptive Maintenance System
Copyright (c) 2026 PT. Kideco Jaya Agung

All rights reserved.

This software and associated documentation files are proprietary and
confidential. Unauthorized copying, distribution, or use of this software,
via any medium, is strictly prohibited without prior written permission
from PT. Kideco Jaya Agung.
```

---

## 📬 Kontak

**PRATYAKSA** dikembangkan oleh tim Engineering AIoT PT. Kideco Jaya Agung.

| | |
|---|---|
| 🏭 **Perusahaan** | PT. Kideco Jaya Agung |
| 🏗️ **Lokasi** | Site Tambang, Kab. Paser, Kalimantan Timur |
| 📧 **Email** | — |
| 🔗 **LinkedIn** | [PT. Kideco Jaya Agung](https://www.linkedin.com/company/pt-kideco-jaya-agung) |

---

<div align="center">

**⛏️ PRATYAKSA — AIoT Predictive + Prescriptive Maintenance**

*Mewujudkan Zero Unplanned Breakdowns melalui Kecerdasan Buatan dan Internet of Things*

</div>
