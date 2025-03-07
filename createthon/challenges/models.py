
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='uploads/category_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    points = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    markdown_content = models.TextField(blank=True)
    code_template = models.TextField(blank=True, help_text="Starter code for the challenge")
    solution = models.TextField(blank=True, help_text="Solution code for validation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    time_limit = models.IntegerField(default=0, help_text="Time limit in seconds (0 for no limit)")
    tags = models.ManyToManyField('ChallengeTag', blank=True)

    def __str__(self):
        return self.title
    
    def validate_submission(self, submission_code):
        # For basic implementation, just check if submission matches solution
        return {
            'passed': submission_code == self.solution,
            'details': 'Submission validated successfully' if submission_code == self.solution else 'Solution does not match expected output'
        }

class ChallengeTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Comment(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.challenge.title}"
