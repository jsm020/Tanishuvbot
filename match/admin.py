from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'liked', 'timestamp')
    search_fields = ('user_from__name', 'user_to__name')
