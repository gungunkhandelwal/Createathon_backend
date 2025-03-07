from django.urls import path, include
from rest_framework.routers import DefaultRouter

from progress.views import (
    UserProgressViewSet,
    AchievementViewSet,
    LeaderboardViewSet
)

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet)
router.register(r'user-progress', UserProgressViewSet, basename='userprogress')
router.register(r'leaderboard', LeaderboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]