from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, fields
from django.utils import timezone

from progress.models import (
    UserProgress, 
    Achievement, 
    UserAchievement, 
    Leaderboard
)
from progress.serializers import (
    UserProgressSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    LeaderboardSerializer
)
from challenges.models import Challenge
from django.contrib.auth import models
from django.contrib.auth.models import User

class UserProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for handling User Progress"""
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return progress only for the current user"""
        return UserProgress.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def user_challenge_summary(self, request):
        """Get summary of user's challenge progress"""
        total_challenges = Challenge.objects.filter(status='published').count()
        completed_challenges = UserProgress.objects.filter(
            user=request.user, 
            status='completed'
        ).count()
        
        in_progress_challenges = UserProgress.objects.filter(
            user=request.user
        ).exclude(
            status='completed'
        ).count()
        
        total_points_earned = UserProgress.objects.filter(
            user=request.user,
            status='completed'
        ).aggregate(
            total=Sum('challenge__points')
        )['total'] or 0
        
        # Get completion by difficulty
        difficulty_stats = UserProgress.objects.filter(
            user=request.user,
            status='completed'
        ).values(
            'challenge__difficulty'
        ).annotate(
            count=Count('id')
        )
        
        difficulty_completion = {
            item['challenge__difficulty']: item['count'] 
            for item in difficulty_stats
        }
        
        # Get category completion stats
        category_stats = UserProgress.objects.filter(
            user=request.user,
            status='completed'
        ).values(
            'challenge__category__name'
        ).annotate(
            count=Count('id')
        )
        
        category_completion = {
            item['challenge__category__name']: item['count'] 
            for item in category_stats
        }
        
        return Response({
            'total_challenges': total_challenges,
            'completed_challenges': completed_challenges,
            'in_progress_challenges': in_progress_challenges,
            'completion_percentage': (completed_challenges / total_challenges) * 100 if total_challenges > 0 else 0,
            'total_points_earned': total_points_earned,
            'difficulty_completion': difficulty_completion,
            'category_completion': category_completion
        })

class AchievementViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Achievements"""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def user_achievements(self, request):
        """Get achievements earned by the current user"""
        user_achievements = UserAchievement.objects.filter(user=request.user)
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def available_achievements(self, request):
        """Get all available achievements with earned status"""
        all_achievements = Achievement.objects.all()
        earned_achievement_ids = UserAchievement.objects.filter(
            user=request.user
        ).values_list('achievement_id', flat=True)
        
        data = []
        for achievement in all_achievements:
            achievement_data = AchievementSerializer(achievement).data
            achievement_data['earned'] = achievement.id in earned_achievement_ids
            data.append(achievement_data)
            
        return Response(data)
    
class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for handling Leaderboard"""
    queryset = Leaderboard.objects.all().order_by('ranking')
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def top_performers(self, request):
        """Get top performers on the leaderboard"""
        limit = int(request.query_params.get('limit', 10))
        top_performers = Leaderboard.objects.all().order_by('ranking')[:limit]
        serializer = LeaderboardSerializer(top_performers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def user_rank(self, request):
        """Get current user's rank on the leaderboard"""
        try:
            user_rank = Leaderboard.objects.get(user=request.user)
            serializer = LeaderboardSerializer(user_rank)
            
            # Get nearby users for context
            nearby_users = Leaderboard.objects.filter(
                ranking__gte=max(1, user_rank.ranking - 2),
                ranking__lte=user_rank.ranking + 2
            ).exclude(id=user_rank.id).order_by('ranking')
            
            nearby_serializer = LeaderboardSerializer(nearby_users, many=True)
            
            return Response({
                'user_rank': serializer.data,
                'nearby_users': nearby_serializer.data
            })
        except Leaderboard.DoesNotExist:
            return Response({'message': 'User not on leaderboard yet'}, status=404)
    
    @action(detail=False, methods=['GET'])
    def category_leaders(self, request):
        """Get leaders by category"""
        from django.db.models import Count, Sum
        
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=400)
            
        # Find users who completed challenges in this category
        category_leaders = User.objects.annotate(
            category_points=Sum(
                'userprogress__challenge__points',
                filter=models.Q(
                    userprogress__status='completed',
                    userprogress__challenge__category_id=category_id
                )
            ),
            challenges_completed=Count(
                'userprogress',
                filter=models.Q(
                    userprogress__status='completed',
                    userprogress__challenge__category_id=category_id
                )
            )
        ).filter(category_points__gt=0).order_by('-category_points', '-challenges_completed')[:10]
        
        result = []
        for i, user in enumerate(category_leaders):
            result.append({
                'rank': i + 1,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'category_points': user.category_points,
                'challenges_completed': user.challenges_completed
            })
            
        return Response(result)
    
    @action(detail=False, methods=['GET'])
    def difficulty_leaders(self, request):
        """Get leaders by difficulty level"""
        difficulty = request.query_params.get('difficulty')
        if not difficulty:
            return Response({'error': 'Difficulty parameter is required'}, status=400)
            
        # Find users who completed challenges of this difficulty
        difficulty_leaders = User.objects.annotate(
            difficulty_points=Sum(
                'userprogress__challenge__points',
                filter=models.Q(
                    userprogress__status='completed',
                    userprogress__challenge__difficulty=difficulty
                )
            ),
            challenges_completed=Count(
                'userprogress',
                filter=models.Q(
                    userprogress__status='completed',
                    userprogress__challenge__difficulty=difficulty
                )
            )
        ).filter(difficulty_points__gt=0).order_by('-difficulty_points', '-challenges_completed')[:10]
        
        result = []
        for i, user in enumerate(difficulty_leaders):
            result.append({
                'rank': i + 1,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'difficulty_points': user.difficulty_points,
                'challenges_completed': user.challenges_completed
            })
            
        return Response(result)
    
    
    @action(detail=False, methods=['GET'])
    def challenge(self, request):
        """Get leaderboard for a specific challenge"""
        challenge_id = request.query_params.get('challenge')
        if not challenge_id:
            return Response({'error': 'Challenge ID is required'}, status=400)
            
        # Find users who completed this challenge, ordered by completion time
        challenge_leaders = UserProgress.objects.filter(
            challenge_id=challenge_id,
            status='completed'
        ).order_by('time_spent').select_related('user')
        
        result = []
        for i, progress in enumerate(challenge_leaders):
            result.append({
                'rank': i + 1,
                'user_id': progress.user.id,
                'username': progress.user.username,
                'time_spent': progress.time_spent,
                'score': progress.score
            })
            
        return Response(result)

