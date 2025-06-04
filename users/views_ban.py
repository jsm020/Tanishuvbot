from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User

class BanUserAPIView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id is required.'}, status=400)
        try:
            user = User.objects.get(telegram_id=telegram_id)
            user.is_banned = True
            user.save()
            return Response({'status': 'banned'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
