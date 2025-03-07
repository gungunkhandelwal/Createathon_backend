from django.urls import path, include
from rest_framework.routers import DefaultRouter

from challenges.views import (
    CategoryViewSet, 
    ChallengeViewSet,
    ChallengeTagViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'tags', ChallengeTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]