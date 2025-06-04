from django.urls import path
from .views import StartChatAPIView, SendMessageAPIView, ChatMessagesAPIView

urlpatterns = [
    path('start/', StartChatAPIView.as_view(), name='chat-start'),
    path('send/', SendMessageAPIView.as_view(), name='chat-send'),
    path('messages/', ChatMessagesAPIView.as_view(), name='chat-messages'),
]
