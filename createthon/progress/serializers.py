from rest_framework import serializers
from progress.models import  Achievement

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'points_required', 'badge_icon']