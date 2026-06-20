# PRATYAKSA: AIoT Predictive Maintenance

Predictive maintenance system for Kideco Pasir Mine heavy equipment. Ingests real-time telemetry to predict Remaining Useful Life (RUL) and detect anomalies using XGBoost, LSTM Experts, and Digital Twin cross-checking.

## Architecture
* **Ingestion:** Redis Streams
* **Inference:** FastAPI + TensorFlow/Keras + XGBoost
* **Storage:** PostgreSQL + TimescaleDB
* **Alerting:** Telegram Bot Alerting System

## Local Deployment
1. Define environment variables in `.env`:
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `POSTGRES_PASSWORD`, etc.
2. Launch the cluster:
   `docker compose up -d`
3. (Optional) Run the local stream simulator to inject test telemetry:
   `python simulator/stream_simulator.py`