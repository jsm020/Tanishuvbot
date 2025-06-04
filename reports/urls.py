from django.urls import path
from .views import ReportAPIView
from .bot_notify_api import ReportNotifyBotAPIView

urlpatterns = [
    path('', ReportAPIView.as_view(), name='report'),
    path('notify/', ReportNotifyBotAPIView.as_view(), name='report-notify-bot'),
]
