
from django.db import models
from users.models import User

class Report(models.Model):
    reporter = models.ForeignKey(User, related_name='reporter', on_delete=models.CASCADE)
    reported = models.ForeignKey(User, related_name='reported', on_delete=models.CASCADE)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
