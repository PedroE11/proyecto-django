from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """Modelo para extender la información del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    grade_level = models.IntegerField(choices=[
        (1, '1° Bachillerato'),
        (2, '2° Bachillerato'),
        (3, '3° Bachillerato')
    ], default=1)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Progress(models.Model):
    """Modelo para el seguimiento del progreso del estudiante"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    total_exercises = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    total_time_spent = models.DurationField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Campos para seguimiento por tipo de operación
    addition_exercises = models.IntegerField(default=0)
    addition_correct = models.IntegerField(default=0)
    subtraction_exercises = models.IntegerField(default=0)
    subtraction_correct = models.IntegerField(default=0)
    multiplication_exercises = models.IntegerField(default=0)
    multiplication_correct = models.IntegerField(default=0)
    division_exercises = models.IntegerField(default=0)
    division_correct = models.IntegerField(default=0)

    def __str__(self):
        return f"Progreso de {self.user.username}"
    
    def accuracy_percentage(self):
        """Calcula el porcentaje de precisión del estudiante"""
        if self.total_exercises == 0:
            return 0
        return round((self.correct_answers / self.total_exercises) * 100, 2)
    
    def operation_accuracy(self, operation_type):
        """Calcula la precisión por tipo de operación"""
        if operation_type == 'addition':
            return self._calculate_percentage(self.addition_correct, self.addition_exercises)
        elif operation_type == 'subtraction':
            return self._calculate_percentage(self.subtraction_correct, self.subtraction_exercises)
        elif operation_type == 'multiplication':
            return self._calculate_percentage(self.multiplication_correct, self.multiplication_exercises)
        elif operation_type == 'division':
            return self._calculate_percentage(self.division_correct, self.division_exercises)
        return 0
    
    def _calculate_percentage(self, correct, total):
        if total == 0:
            return 0
        return round((correct / total) * 100, 2)

class ActivityLog(models.Model):
    """Modelo para registrar la actividad del usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"

# Señales para crear automáticamente un perfil y un registro de progreso cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Progress.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()