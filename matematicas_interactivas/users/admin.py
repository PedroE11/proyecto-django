from django.contrib import admin
from .models import Profile, Progress, ActivityLog

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_level', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('grade_level', 'created_at')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_exercises', 'correct_answers', 'accuracy_percentage', 'last_activity')
    search_fields = ('user__username',)
    list_filter = ('last_activity',)
    
    def accuracy_percentage(self, obj):
        return f"{obj.accuracy_percentage()}%"
    accuracy_percentage.short_description = 'Precisión'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp')
    search_fields = ('user__username', 'activity_type')
    list_filter = ('activity_type', 'timestamp')