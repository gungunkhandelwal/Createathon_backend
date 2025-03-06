from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from challenges.models import Challenge, Category
from progress.models import UserProgress, Achievement, UserAchievement
from challenges.serializers import (
    ChallengeSerializer, 
    CategorySerializer, 
    UserProgressSerializer
)
from rest_framework.permissions import IsAuthenticated
from progress.serializers import AchievementSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Category operations
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Challenge operations with additional custom actions
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter challenges by difficulty or category
        """
        queryset = Challenge.objects.all()
        difficulty = self.request.query_params.get('difficulty', None)
        category = self.request.query_params.get('category', None)

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if category:
            queryset = queryset.filter(category__name=category)
        
        return queryset

    @action(detail=True, methods=['GET'],url_path='challenge-details')
    def challenge_details(self, request, pk=None):
        """
        Fetch challenge details with user progress
        """
        challenge = self.get_object()
        user_progress = UserProgress.objects.filter(user=request.user, challenge=challenge).first()
        challenge_data = self.get_serializer(challenge).data
        progress_data = UserProgressSerializer(user_progress).data if user_progress else None

        return Response({
            'challenge': challenge_data,
            'user_progress': progress_data
        })

    @action(detail=True, methods=['POST'])
    def start_challenge(self, request, pk=None):
        """
        Custom action to start a challenge for the current user
        """
        challenge = self.get_object()
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user, 
            challenge=challenge,
            defaults={'status': 'started'}
        )

        if not created:
            user_progress.attempts += 1
            user_progress.save()

        serializer = UserProgressSerializer(user_progress)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def submit_challenge(self, request, pk=None):
        """
        Submit a challenge solution
        """
        challenge = self.get_object()
        submission_code = request.data.get('submission_code', '')

        user_progress, _ = UserProgress.objects.get_or_create(
            user=request.user, 
            challenge=challenge
        )

        # Here you would typically add validation logic
        # For now, we'll just update status
        user_progress.status = 'submitted'
        user_progress.submission_code = submission_code
        user_progress.save()
        # Basic Validation Result - Replace with your actual evaluation logic
        validation_result = {'passed': submission_code == challenge.solution, 'details': ''}  # Example
        user_progress.status = 'completed' if validation_result['passed'] else 'failed'
        user_progress.save()

        serializer = UserProgressSerializer(user_progress)
        return Response({
            'user_progress': serializer.data,
            'validation_result': validation_result
        })

class UserProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling User Progress
    """
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return progress only for the current user
        """
        return UserProgress.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def user_challenge_summary(self, request):
        """
        Get summary of user's challenge progress
        """
        total_challenges = Challenge.objects.count()
        completed_challenges = UserProgress.objects.filter(
            user=request.user, 
            status='completed'
        ).count()

        return Response({
            'total_challenges': total_challenges,
            'completed_challenges': completed_challenges,
            'completion_percentage': (completed_challenges / total_challenges) * 100 if total_challenges > 0 else 0
        })
