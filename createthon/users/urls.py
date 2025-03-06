from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users.views import (
    UserRegistrationView,
    AuthViewSet
)
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'auth',AuthViewSet,basename='auth')

urlpatterns = [
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('api/',include(router.urls))
]