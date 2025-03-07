from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Sum

from challenges.models import Category, Challenge, Comment, ChallengeTag
from progress.models import UserProgress, Leaderboard
from challenges.serializers import (
    CategorySerializer, 
    ChallengeSerializer,
    ChallengeDetailSerializer,
    CommentSerializer,
    ChallengeTagSerializer
)
from progress.serializers import UserProgressSerializer, LeaderboardSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Category operations"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def with_challenge_count(self, request):
        """Return categories with challenge counts"""
        categories = Category.objects.annotate(challenge_count=Count('challenge'))
        data = [{
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon.url if category.icon else None,
            'challenge_count': category.challenge_count
        } for category in categories]
        return Response(data)

class ChallengeTagViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Challenge Tags"""
    queryset = ChallengeTag.objects.all()
    serializer_class = ChallengeTagSerializer
    permission_classes = [permissions.IsAuthenticated]

class ChallengeViewSet(viewsets.ModelViewSet):
    """ViewSet for handling Challenge operations with additional custom actions"""
    queryset = Challenge.objects.filter(status='published')
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'challenge_details':
            return ChallengeDetailSerializer
        return ChallengeSerializer

    def get_queryset(self):
        """Optionally filter challenges by difficulty, category, or tags"""
        queryset = Challenge.objects.filter(status='published')
        difficulty = self.request.query_params.get('difficulty')
        category = self.request.query_params.get('category')
        tags = self.request.query_params.getlist('tags')
        search = self.request.query_params.get('search')

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if category:
            queryset = queryset.filter(category__id=category)
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['GET'], url_path='challenge-details')
    def challenge_details(self, request, pk=None):
        """Fetch challenge details with user progress"""
        challenge = self.get_object()
        user_progress = UserProgress.objects.filter(
            user=request.user, 
            challenge=challenge
        ).first()
        
        challenge_data = self.get_serializer(challenge).data
        progress_data = UserProgressSerializer(user_progress).data if user_progress else None

        return Response({
            'challenge': challenge_data,
            'user_progress': progress_data
        })

    @action(detail=True, methods=['POST'])
    def start_challenge(self, request, pk=None):
        """Custom action to start a challenge for the current user"""
        challenge = self.get_object()
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user, 
            challenge=challenge,
            defaults={'status': 'started', 'start_time': timezone.now()}
        )

        if not created and user_progress.status != 'completed':
            user_progress.attempts += 1
            user_progress.save()

        serializer = UserProgressSerializer(user_progress)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def submit_challenge(self, request, pk=None):
        """Submit a challenge solution"""
        challenge = self.get_object()
        submission_code = request.data.get('submission_code', '')
        time_spent = request.data.get('time_spent', 0)

        # Get or create user progress
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user, 
            challenge=challenge,
            defaults={'status': 'started', 'start_time': timezone.now()}
        )

        # Update progress
        user_progress.status = 'submitted'
        user_progress.submission_code = submission_code
        user_progress.time_spent += int(time_spent)  # Accumulate time spent
        user_progress.attempts += 1
        user_progress.last_attempt_time = timezone.now()
        user_progress.save()
        
        # Validate submission
        validation_result = challenge.validate_submission(submission_code)
        
        # Update status based on validation
        if validation_result['passed']:
            previous_status = user_progress.status
            user_progress.mark_completed()
            
            # Only update leaderboard if this is the first time completing the challenge
            if previous_status != 'completed':
                # Update leaderboard
                self._update_user_leaderboard(request.user)
        else:
            user_progress.status = 'failed'
            user_progress.save()

        serializer = UserProgressSerializer(user_progress)
        return Response({
            'user_progress': serializer.data,
            'validation_result': validation_result
        })
    
    def _update_user_leaderboard(self, user):
        """Update a specific user's leaderboard entry"""
        # Calculate total points
        total_points = UserProgress.objects.filter(
            user=user,
            status='completed'
        ).aggregate(
            total=Sum('challenge__points')
        )['total'] or 0
        
        # Count completed challenges
        challenges_completed = UserProgress.objects.filter(
            user=user,
            status='completed'
        ).count()
        
        # Update or create leaderboard entry
        leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
        leaderboard.total_points = total_points
        leaderboard.challenges_completed = challenges_completed
        leaderboard.save()
        
        # Update rankings for all users
        self._update_leaderboard_rankings()
    
    def _update_leaderboard_rankings(self):
        """Update rankings on the leaderboard"""
        # First order by points, then by number of challenges completed (for tie-breaking)
        leaderboards = Leaderboard.objects.all().order_by('-total_points', '-challenges_completed')
        
        for i, leaderboard in enumerate(leaderboards):
            if leaderboard.ranking != i + 1:  # Only update if ranking changed
                leaderboard.ranking = i + 1
                leaderboard.save()
    
    @action(detail=True, methods=['POST'])
    def add_comment(self, request, pk=None):
        """Add a comment to a challenge"""
        challenge = self.get_object()
        text = request.data.get('text')
        parent_id = request.data.get('parent_id')
        
        if not text:
            return Response({'error': 'Comment text is required'}, status=400)
        
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, challenge=challenge)
            except Comment.DoesNotExist:
                return Response({'error': 'Parent comment not found'}, status=404)
        
        comment = Comment.objects.create(
            challenge=challenge,
            user=request.user,
            text=text,
            parent=parent
        )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data)