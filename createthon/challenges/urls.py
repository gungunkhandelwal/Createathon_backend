from django.urls import path, include
from rest_framework.routers import DefaultRouter

from challenges.views import (
    CategoryViewSet, 
    ChallengeViewSet, 
    UserProgressViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    CustomTokenObtainPairView, 
    UserRegistrationView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'progress', UserProgressViewSet, basename='userprogress')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User Registration
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('', include(router.urls)),
]