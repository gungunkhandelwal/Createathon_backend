from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from progress.models import  Achievement, UserAchievement
from progress.serializers import ( 
    AchievementSerializer
)

class AchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Achievements
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def user_achievements(self, request):
        """
        Get achievements earned by the current user
        """
        user_achievements = UserAchievement.objects.filter(user=request.user)
        serializer = AchievementSerializer([ua.achievement for ua in user_achievements], many=True)
        return Response(serializer.data)