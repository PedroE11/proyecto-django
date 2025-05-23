from django.contrib import admin
from .models import Category, DifficultyLevel, Exercise, ExerciseSession, ExerciseAttempt

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    list_filter = ('value',)
    search_fields = ('name',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'operation_type', 'difficulty', 'category')
    list_filter = ('operation_type', 'difficulty', 'category')
    search_fields = ('question',)

class ExerciseAttemptInline(admin.TabularInline):
    model = ExerciseAttempt
    extra = 0
    readonly_fields = ('exercise', 'user_answer', 'is_correct', 'time_taken', 'created_at')

@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'total_exercises', 'correct_answers', 'accuracy')
    list_filter = ('user', 'start_time', 'difficulty', 'category')
    search_fields = ('user__username',)
    inlines = [ExerciseAttemptInline]
    
    def accuracy(self, obj):
        return f"{obj.accuracy()}%"
    accuracy.short_description = 'Precisión'

@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ('session', 'exercise', 'user_answer', 'is_correct', 'time_taken')
    list_filter = ('is_correct', 'session__user')
    search_fields = ('session__user__username', 'exercise__question')