from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserRegisterSerializer, UserShortSerializer
from match.models import Match
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

class FriendsListAPIView(APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id param is required.'}, status=400)
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        # Do'stlar: o'zaro like bosilganlar
        matches = Match.objects.filter(user_from=user, liked=True)
        friends = []
        for m in matches:
            if Match.objects.filter(user_from=m.user_to, user_to=user, liked=True).exists():
                friends.append(m.user_to)
        serializer = UserShortSerializer(friends, many=True)
        return Response(serializer.data)
class NearbyUsersAPIView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response({'error': 'lat and lon are required and must be float.'}, status=400)

        # Haversine formula
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # km
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c

        users = []
        for user in User.objects.filter(is_banned=False):
            distance = haversine(lat, lon, user.latitude, user.longitude)
            if distance <= 50:  # 50 km radius
                users.append(user)
        serializer = UserShortSerializer(users, many=True)
        return Response(serializer.data)

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
