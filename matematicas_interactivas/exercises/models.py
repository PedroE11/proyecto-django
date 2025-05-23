from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """Modelo para categorías de ejercicios matemáticos"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class DifficultyLevel(models.Model):
    """Modelo para niveles de dificultad"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    value = models.IntegerField(default=1)  # 1: Fácil, 2: Medio, 3: Difícil
    
    def __str__(self):
        return self.name

class Exercise(models.Model):
    """Modelo para ejercicios matemáticos"""
    OPERATION_CHOICES = [
        ('addition', 'Suma'),
        ('subtraction', 'Resta'),
        ('multiplication', 'Multiplicación'),
        ('division', 'División'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exercises')
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, related_name='exercises')
    operation_type = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    question = models.CharField(max_length=255)
    answer = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.question} = {self.answer}"

class ExerciseSession(models.Model):
    """Modelo para sesiones de ejercicios"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_exercises = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True, related_name='sessions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='sessions')
    
    def __str__(self):
        return f"Sesión de {self.user.username} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    def duration(self):
        """Calcula la duración de la sesión"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time
    
    def accuracy(self):
        """Calcula el porcentaje de precisión"""
        if self.total_exercises == 0:
            return 0
        return round((self.correct_answers / self.total_exercises) * 100, 2)
    
    def is_active(self):
        """Verifica si la sesión está activa"""
        return self.end_time is None

class ExerciseAttempt(models.Model):
    """Modelo para intentos de resolución de ejercicios"""
    session = models.ForeignKey(ExerciseSession, on_delete=models.CASCADE, related_name='attempts')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='attempts')
    user_answer = models.DecimalField(max_digits=10, decimal_places=2)
    is_correct = models.BooleanField(default=False)
    time_taken = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Intento de {self.session.user.username} - {self.exercise.question}"