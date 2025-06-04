from backend.celery import app
import requests

@app.task
def notify_admin_via_telegram(data):
    BOT_NOTIFY_URL = 'http://localhost:8000/api/report/notify/'
    try:
        requests.post(BOT_NOTIFY_URL, json=data, timeout=5)
    except Exception as e:
        print('Botga xabar yuborilmadi:', e)
