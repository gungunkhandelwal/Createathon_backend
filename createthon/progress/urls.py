from django.urls import path, include
from rest_framework.routers import DefaultRouter

from progress.views import (
    AchievementViewSet
)

router = DefaultRouter()
router.register(r'achievements', AchievementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]