
from rest_framework import serializers
from progress.models import UserProgress, Achievement, UserAchievement, Leaderboard
from challenges.serializers import ChallengeSerializer,UserBasicSerializer
from challenges.models import Challenge

class UserProgressSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    challenge_id = serializers.PrimaryKeyRelatedField(
        queryset=Challenge.objects.all(),
        source='challenge',
        write_only=True
    )
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'challenge', 'challenge_id', 'status', 'attempts', 
            'completed_at', 'submission_code', 'start_time',
            'last_attempt_time', 'time_spent'
        ]

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'points_required', 'badge_icon']

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']

class LeaderboardSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = ['id', 'user', 'total_points', 'challenges_completed', 'ranking']
