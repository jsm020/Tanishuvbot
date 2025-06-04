from django.urls import path
from .views import RegisterAPIView, NearbyUsersAPIView, FriendsListAPIView
from .views_ban import BanUserAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('users/nearby/', NearbyUsersAPIView.as_view(), name='users-nearby'),
    path('friends/', FriendsListAPIView.as_view(), name='friends-list'),
    path('users/ban/', BanUserAPIView.as_view(), name='ban-user'),
]
