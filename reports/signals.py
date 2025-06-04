from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import requests
from .models import Report

@receiver(post_save, sender=Report)
def notify_admin_on_report(sender, instance, created, **kwargs):
    if created:
        # 1. Email orqali xabar (ixtiyoriy)
        subject = 'Yangi shikoyat (Report)'
        message = f"Shikoyatchi: {instance.reporter}\nShikoyat qilinuvchi: {instance.reported}\nSabab: {instance.reason}\nVaqt: {instance.timestamp}"
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

        # 2. Telegram botga xabar yuborish (POST so'rov)
        # Bu URL va TOKEN ni o'zgartiring!
        # Django ichidagi endpointga POST yuboriladi (localhost)
        BOT_NOTIFY_URL = 'http://localhost:8000/api/report/notify/'
        data = {
            'report_id': instance.id,
            'reporter': str(instance.reporter),
            'reported': str(instance.reported),
            'reason': instance.reason,
            'timestamp': str(instance.timestamp),
        }
        try:
            requests.post(BOT_NOTIFY_URL, json=data, timeout=5)
        except Exception as e:
            print('Botga xabar yuborilmadi:', e)
