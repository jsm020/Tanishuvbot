from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Match
from .serializers import MatchSerializer
from users.models import User

class LikeAPIView(APIView):
    def post(self, request):
        user_from_id = request.data.get('user_from')
        user_to_id = request.data.get('user_to')
        if not user_from_id or not user_to_id:
            return Response({'error': 'user_from and user_to are required.'}, status=400)
        try:
            user_from = User.objects.get(telegram_id=user_from_id)
            user_to = User.objects.get(telegram_id=user_to_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        match, created = Match.objects.get_or_create(user_from=user_from, user_to=user_to)
        match.liked = True
        match.save()
        serializer = MatchSerializer(match)
        return Response(serializer.data, status=201 if created else 200)
