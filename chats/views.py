from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from users.models import User
# views.py (Django)
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def check_user(request):
    telegram_id = request.data.get('telegram_id')
    exists = User.objects.filter(telegram_id=telegram_id).exists()
    return Response({'exists': exists})
class ChatMessagesAPIView(APIView):
    def get(self, request):
        chat_id = request.query_params.get('chat')
        if not chat_id:
            return Response({'error': 'chat param is required.'}, status=400)
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found.'}, status=404)
        messages = Message.objects.filter(chat=chat).order_by('-timestamp')[:50][::-1]  # last 50, ascending
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class StartChatAPIView(APIView):
    def post(self, request):
        user1_id = request.data.get('user1')
        user2_id = request.data.get('user2')
        if not user1_id or not user2_id:
            return Response({'error': 'user1 and user2 are required.'}, status=400)
        try:
            user1 = User.objects.get(telegram_id=user1_id)
            user2 = User.objects.get(telegram_id=user2_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        chat, created = Chat.objects.get_or_create(user1=user1, user2=user2, is_active=True)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=201 if created else 200)

class SendMessageAPIView(APIView):
    def post(self, request):
        chat_id = request.data.get('chat')
        sender_id = request.data.get('sender')
        content = request.data.get('content')
        if not chat_id or not sender_id or not content:
            return Response({'error': 'chat, sender, and content are required.'}, status=400)
        try:
            chat = Chat.objects.get(id=chat_id, is_active=True)
            sender = User.objects.get(telegram_id=sender_id)
        except (Chat.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Chat or sender not found.'}, status=404)
        message = Message.objects.create(chat=chat, sender=sender, content=content)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=201)
