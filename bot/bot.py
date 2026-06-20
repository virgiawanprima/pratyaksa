"""
PRATYAKSA Telegram Bot v1.3
Persistent alert ID via Redis, Fleet Status Command, & Auto-Reconnect
- Perbaikan: koneksi Redis global (tidak bocor), tanpa FastAPI
"""
import asyncio
import os
import json
import redis.asyncio as aioredis
import httpx
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("PRATYAKSA-BOT")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum diset!")
    exit(1)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# ── Koneksi Redis persistent ─────────────────────────────────────────────────
async def connect_redis() -> aioredis.Redis:
    """Membuka koneksi Redis dengan retry sampai berhasil."""
    while True:
        try:
            r = await aioredis.from_url(REDIS_URL, decode_responses=False)
            await r.ping()
            logger.info("Bot terhubung ke Redis.")
            return r
        except Exception as e:
            logger.error(f"Menunggu Redis... ({e})")
            await asyncio.sleep(5)

# ── TUGAS 1: Pantau Redis stream:alerts ───────────────────────────────────────
async def pantau_redis(r: aioredis.Redis, client: httpx.AsyncClient):
    # Load last processed ID dari Redis agar persistent lintas restart
    last_id_raw = await r.get("bot:last_alert_id")
    last_id     = last_id_raw.decode() if last_id_raw else "0"
    logger.info(f"Melanjutkan dari alert ID: {last_id}")

    while True:
        try:
            alerts = await r.xread(
                {"stream:alerts": last_id},
                block=5000,
                count=10
            )

            if not alerts:
                continue

            for _, messages in alerts:
                for msg_id, data in messages:
                    d = {
                        k.decode('utf-8'): v.decode('utf-8')
                        for k, v in data.items()
                    }

                    message = (
                        f"🚨<b>[URGENT ALARM : PRATYAKSA]</b>🚨\n\n"
                        f"🚜 <b>Unit:</b> {d.get('asset_id', 'N/A')} ({d.get('model', 'N/A')})\n"
                        f"📍 <b>Lokasi:</b> {d.get('lokasi', 'N/A')}\n"
                        f"⚠️ <b>Status:</b> {d.get('status', 'N/A')} "
                        f"(Estimasi Sisa Umur: {d.get('rul', '0')} Jam)\n\n"
                        f"🔍 <b>Analisis Kerusakan AI (SHAP):</b>\n"
                        f"1. {d.get('shap1', 'N/A')}\n"
                        f"2. {d.get('shap2', 'N/A')}\n\n"
                        f"🛠️ <b>Rekomendasi Tindakan:</b>\n"
                        f"Arahkan unit ke Workshop Pit terdekat sebelum breakdown. "
                        f"Lakukan inspeksi dan penggantian komponen yang terdampak.\n\n"
                        f"📦 <b>Info Suku Cadang:</b>\n"
                        f"- Part Name: {d.get('part_name', 'N/A')}\n"
                        f"- Part No: {d.get('part_no', 'N/A')}\n"
                        f"- Stok Workshop B: {d.get('stok', '0')} Unit\n\n"
                        f"🔗 <a href=\"https://pratyaksa.kideco.co.id/wo/generate/"
                        f"{d.get('asset_id')}\">Buat Work Order di CMMS</a>"
                    )

                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    try:
                        response = await client.post(
                            url,
                            json={
                                "chat_id":    CHAT_ID,
                                "text":       message,
                                "parse_mode": "HTML",
                            },
                            timeout=10,
                        )
                        if response.status_code == 200:
                            logger.info(f"Alert terkirim: {d.get('asset_id')}")
                        else:
                            logger.error(f"Gagal kirim Telegram: {response.text}")
                    except Exception as e:
                        logger.error(f"HTTP error kirim alert: {e}")

                    # Update last_id dan persist ke Redis
                    last_id = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                    await r.set("bot:last_alert_id", last_id)

        except Exception as e:
            logger.error(f"Error loop Redis: {e}")
            await asyncio.sleep(5)


# ── TUGAS 2: Polling Telegram commands ────────────────────────────────────────
async def pantau_telegram(r: aioredis.Redis, client: httpx.AsyncClient):
    offset = None
    logger.info("Bot siap menerima pesan Telegram...")

    while True:
        try:
            url    = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"timeout": 10, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset

            response = await client.get(url, params=params, timeout=15)

            if response.status_code != 200:
                await asyncio.sleep(5)
                continue

            data = response.json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1

                msg            = update.get("message", {})
                text           = msg.get("text", "")
                chat_id_sender = msg.get("chat", {}).get("id")

                if not chat_id_sender:
                    continue

                if text == "/start":
                    await _kirim_welcome(client, chat_id_sender)
                elif text == "/status":
                    await _kirim_status(r, client, chat_id_sender)

        except Exception as e:
            logger.error(f"Error polling Telegram: {e}")

        await asyncio.sleep(1)


async def _kirim_welcome(client: httpx.AsyncClient, chat_id: int):
    welcome_msg = (
        "⚡ <b>SYSTEM ONLINE: PRATYAKSA Command Center</b> ⚡\n"
        "<i>Engineered by Oryphem</i>\n\n"
        "Selamat datang! Anda telah terhubung dengan asisten "
        "<i>Predictive Maintenance</i> berbasis AI.\n\n"
        "<b>Tujuan utama:</b> Zero Breakdown, Meminimalisir Unplanned Downtime, "
        "dan Memaksimalkan Profit Operasional tambang Anda. 📈💰\n\n"
        "<b>Kapabilitas Sistem:</b>\n"
        "📡 <b>Real-time Telemetry</b> — memantau sensor unit 24/7\n"
        "🧠 <b>Smart Diagnostics (SHAP)</b> — ungkap akar masalah sebelum breakdown\n"
        "🛠️ <b>CMMS Ready</b> — eskalasi alarm jadi Work Order 1 klik\n\n"
        "Ketik /status untuk melihat ringkasan fleet saat ini.\n\n"
        "Status AI: <code>[ACTIVE]</code> 🚜💻"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        await client.post(
            url,
            json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "HTML"},
            timeout=10,
        )
        logger.info(f"Welcome sent to {chat_id}")
    except Exception as e:
        logger.error(f"Error kirim welcome: {e}")


async def _kirim_status(r: aioredis.Redis, client: httpx.AsyncClient, chat_id: int):
    """Query Redis untuk ringkasan status fleet (menggunakan koneksi yang sama)."""
    try:
        keys = []
        async for key in r.scan_iter(match="result:*", count=100):
            keys.append(key)

        total    = len(keys)
        critical = 0
        warning  = 0

        for key in keys:
            raw = await r.get(key)
            if raw:
                try:
                    result = json.loads(raw)
                    level  = result.get("risk_level", "NORMAL")
                    if level == "CRITICAL":
                        critical += 1
                    elif level == "WARNING":
                        warning += 1
                except Exception:
                    pass

        normal = total - critical - warning
        msg = (
            f"📊 <b>PRATYAKSA Fleet Status</b>\n\n"
            f"🔴 CRITICAL : {critical} unit\n"
            f"🟡 WARNING  : {warning} unit\n"
            f"🟢 NORMAL   : {normal} unit\n"
            f"─────────────────\n"
            f"📦 Total Aktif : {total} unit\n\n"
            f"<i>Data diperbarui real-time dari Redis cache.</i>"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        await client.post(
            url,
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
        logger.info(f"Status sent to {chat_id}")
    except Exception as e:
        logger.error(f"Error kirim status: {e}")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        await client.post(
            url,
            json={
                "chat_id":    chat_id,
                "text":       "❌ Gagal mengambil status fleet. Redis tidak tersedia.",
                "parse_mode": "HTML",
            },
            timeout=10,
        )


# ── Main ───────────────────────────────────────────────────────────────────────
async def run_bot():
    # Buka koneksi Redis persistent
    redis_conn = await connect_redis()
    try:
        async with httpx.AsyncClient() as client:
            await asyncio.gather(
                pantau_redis(redis_conn, client),
                pantau_telegram(redis_conn, client),
            )
    finally:
        await redis_conn.aclose()
        logger.info("Koneksi Redis ditutup.")


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot dihentikan.")