from django.db import models
from django.contrib.auth.models import User
from challenges.models import Challenge
from django.utils import timezone

class UserProgress(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    attempts = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    submission_code = models.TextField(blank=True)
    start_time = models.DateTimeField(auto_now_add=True,null=True)
    last_attempt_time = models.DateTimeField(auto_now=True)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def __str__(self):
        return f"{self.user.username}'s progress on {self.challenge.title}"
    
    def mark_completed(self):
        """Mark the challenge as completed and record completion time"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Check for newly earned achievements
        total_points = UserProgress.objects.filter(
            user=self.user, 
            status='completed'
        ).aggregate(
            total_points=models.Sum('challenge__points')
        )['total_points'] or 0
        
        # Check if user qualifies for any new achievements
        achievements = Achievement.objects.filter(
            points_required__lte=total_points
        ).exclude(
            userachievement__user=self.user
        )
        
        # Award new achievements
        for achievement in achievements:
            UserAchievement.objects.create(
                user=self.user,
                achievement=achievement
            )

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    badge_icon = models.ImageField(upload_to='uploads/achievements/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    ranking = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points', 'ranking']
    
    def __str__(self):
        return f"{self.user.username}'s leaderboard entry"