from django.contrib import admin
from progress.models import UserAchievement,UserProgress,Achievement

admin.site.register(UserProgress)
admin.site.register(UserAchievement)
admin.site.register(Achievement)
