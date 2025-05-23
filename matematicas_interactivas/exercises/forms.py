from django import forms
from .models import Category, DifficultyLevel

class ExerciseConfigForm(forms.Form):
    """Formulario para configurar una sesión de ejercicios"""
    OPERATION_CHOICES = [
        ('all', 'Todas las operaciones'),
        ('addition', 'Suma'),
        ('subtraction', 'Resta'),
        ('multiplication', 'Multiplicación'),
        ('division', 'División'),
    ]
    
    NUMBER_OF_EXERCISES_CHOICES = [
        (5, '5 ejercicios'),
        (10, '10 ejercicios'),
        (15, '15 ejercicios'),
        (20, '20 ejercicios'),
    ]
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    difficulty = forms.ModelChoiceField(
        queryset=DifficultyLevel.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    operation_type = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    number_of_exercises = forms.ChoiceField(
        choices=NUMBER_OF_EXERCISES_CHOICES,
        required=True,
        initial=10,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ExerciseAnswerForm(forms.Form):
    """Formulario para responder un ejercicio"""
    answer = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'autofocus': 'autofocus'})
    )