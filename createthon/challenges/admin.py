from django.contrib import admin
from challenges.models import Category,Challenge,ChallengeTag,Comment

admin.site.register(Challenge)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(ChallengeTag)
