from rest_framework import serializers
from challenges.models import Challenge, Category
from progress.models import UserProgress

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ChallengeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Challenge
        fields = ['id', 'title', 'description', 'difficulty', 
                  'points', 'category', 'created_at', 'markdown_content']
        
class UserProgressSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'challenge', 'status', 'attempts', 
                  'completed_at', 'submission_code']