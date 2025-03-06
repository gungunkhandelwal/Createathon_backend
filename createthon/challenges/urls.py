from django.urls import path, include
from rest_framework.routers import DefaultRouter

from challenges.views import (
    CategoryViewSet, 
    ChallengeViewSet, 
    UserProgressViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'challenge', ChallengeViewSet)
router.register(r'progress', UserProgressViewSet, basename='userprogress')

urlpatterns = [
    path('', include(router.urls)),
]