
from django.db import models
from users.models import User

class Match(models.Model):
    user_from = models.ForeignKey(User, related_name='sent_likes', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='received_likes', on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
