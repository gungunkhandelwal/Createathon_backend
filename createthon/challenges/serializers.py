from rest_framework import serializers
from challenges.models import Challenge, Category, Comment, ChallengeTag
from progress.models import UserProgress
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon']

class ChallengeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeTag
        fields = ['id', 'name']

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CommentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'parent', 'replies']
    
    def get_replies(self, obj):
        if not obj.replies.exists():
            return []
        return CommentSerializer(obj.replies.all(), many=True).data

class ChallengeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category',
        write_only=True
    )
    tags = ChallengeTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'difficulty', 
            'points', 'category', 'category_id', 'created_at', 
            'markdown_content', 'code_template', 'status',
            'time_limit', 'tags'
        ]
        
class ChallengeDetailSerializer(ChallengeSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(ChallengeSerializer.Meta):
        fields = ChallengeSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        # Get only top-level comments (no parent)
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True).data