import random
import time
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Sum, Count

from .models import Category, DifficultyLevel, Exercise, ExerciseSession, ExerciseAttempt
from .forms import ExerciseConfigForm, ExerciseAnswerForm
from users.models import ActivityLog

def generate_exercise(operation_type, difficulty_level):
    """Genera un ejercicio matemático aleatorio"""
    # Definir rangos según dificultad
    if difficulty_level.value == 1:  # Fácil
        num1_range = (1, 10)
        num2_range = (1, 10)
    elif difficulty_level.value == 2:  # Medio
        num1_range = (10, 50)
        num2_range = (10, 50)
    else:  # Difícil
        num1_range = (50, 100)
        num2_range = (50, 100)
    
    # Generar números aleatorios
    num1 = random.randint(*num1_range)
    num2 = random.randint(*num2_range)
    
    # Generar ejercicio según operación
    if operation_type == 'addition':
        question = f"{num1} + {num2}"
        answer = num1 + num2
    elif operation_type == 'subtraction':
        # Asegurar que el resultado sea positivo
        if num1 < num2:
            num1, num2 = num2, num1
        question = f"{num1} - {num2}"
        answer = num1 - num2
    elif operation_type == 'multiplication':
        question = f"{num1} × {num2}"
        answer = num1 * num2
    elif operation_type == 'division':
        # Asegurar que la división sea exacta
        product = num1 * num2
        question = f"{product} ÷ {num1}"
        answer = num2
    else:
        raise ValueError(f"Tipo de operación no válido: {operation_type}")
    
    return {
        'question': question,
        'answer': Decimal(str(answer)),
        'operation_type': operation_type
    }

@login_required
def exercise_config(request):
    """Vista para configurar una sesión de ejercicios"""
    # Crear categorías y niveles de dificultad si no existen
    if Category.objects.count() == 0:
        Category.objects.create(name="Aritmética Básica", description="Operaciones aritméticas básicas")
    
    if DifficultyLevel.objects.count() == 0:
        DifficultyLevel.objects.create(name="Fácil", description="Números del 1 al 10", value=1)
        DifficultyLevel.objects.create(name="Medio", description="Números del 10 al 50", value=2)
        DifficultyLevel.objects.create(name="Difícil", description="Números del 50 al 100", value=3)
    
    if request.method == 'POST':
        form = ExerciseConfigForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            category = form.cleaned_data.get('category')
            difficulty = form.cleaned_data.get('difficulty')
            operation_type = form.cleaned_data.get('operation_type')
            number_of_exercises = int(form.cleaned_data.get('number_of_exercises'))
            
            # Crear sesión de ejercicios
            session = ExerciseSession.objects.create(
                user=request.user,
                total_exercises=number_of_exercises,
                difficulty=difficulty,
                category=category
            )
            
            # Registrar actividad
            ActivityLog.objects.create(
                user=request.user,
                activity_type='inicio_sesion_ejercicios',
                description=f"Inició una sesión de {number_of_exercises} ejercicios de {difficulty.name}"
            )
            
            # Guardar configuración en sesión
            request.session['exercise_session_id'] = session.id
            request.session['operation_type'] = operation_type
            request.session['exercises_remaining'] = number_of_exercises
            request.session['exercise_start_time'] = time.time()
            
            return redirect('exercise_solve')
    else:
        form = ExerciseConfigForm()
    
    return render(request, 'exercises/config.html', {'form': form})

@login_required
def exercise_solve(request):
    """Vista para resolver ejercicios"""
    # Verificar si hay una sesión activa
    session_id = request.session.get('exercise_session_id')
    if not session_id:
        messages.error(request, "No hay una sesión de ejercicios activa.")
        return redirect('exercise_config')
    
    session = get_object_or_404(ExerciseSession, id=session_id, user=request.user)
    operation_type = request.session.get('operation_type', 'all')
    exercises_remaining = request.session.get('exercises_remaining', 0)
    
    # Verificar si quedan ejercicios
    if exercises_remaining <= 0:
        # Finalizar sesión
        session.end_time = timezone.now()
        session.save()
        
        # Registrar actividad
        ActivityLog.objects.create(
            user=request.user,
            activity_type='fin_sesion_ejercicios',
            description=f"Completó una sesión de ejercicios con {session.correct_answers}/{session.total_exercises} respuestas correctas"
        )
        
        # Actualizar progreso del usuario
        progress = request.user.progress.first()
        if progress:
            progress.total_exercises += session.total_exercises
            progress.correct_answers += session.correct_answers
            
            # Actualizar estadísticas por tipo de operación
            for attempt in session.attempts.all():
                op_type = attempt.exercise.operation_type
                if op_type == 'addition':
                    progress.addition_exercises += 1
                    if attempt.is_correct:
                        progress.addition_correct += 1
                elif op_type == 'subtraction':
                    progress.subtraction_exercises += 1
                    if attempt.is_correct:
                        progress.subtraction_correct += 1
                elif op_type == 'multiplication':
                    progress.multiplication_exercises += 1
                    if attempt.is_correct:
                        progress.multiplication_correct += 1
                elif op_type == 'division':
                    progress.division_exercises += 1
                    if attempt.is_correct:
                        progress.division_correct += 1
            
            progress.save()
        
        # Limpiar sesión
        del request.session['exercise_session_id']
        del request.session['operation_type']
        del request.session['exercises_remaining']
        if 'exercise_start_time' in request.session:
            del request.session['exercise_start_time']
        
        return redirect('exercise_results', session_id=session.id)
    
    # Generar ejercicio
    if operation_type == 'all':
        # Seleccionar una operación aleatoria
        operations = ['addition', 'subtraction', 'multiplication', 'division']
        selected_operation = random.choice(operations)
    else:
        selected_operation = operation_type
    
    exercise_data = generate_exercise(selected_operation, session.difficulty)
    
    # Crear o obtener categoría
    category, _ = Category.objects.get_or_create(name="Aritmética Básica")
    
    # Guardar ejercicio en la base de datos
    exercise = Exercise.objects.create(
        category=category,
        difficulty=session.difficulty,
        operation_type=exercise_data['operation_type'],
        question=exercise_data['question'],
        answer=exercise_data['answer']
    )
    
    if request.method == 'POST':
        form = ExerciseAnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            is_correct = user_answer == exercise_data['answer']
            
            # Calcular tiempo tomado
            start_time = request.session.get('exercise_start_time', time.time())
            time_taken = timedelta(seconds=int(time.time() - start_time))
            
            # Guardar intento
            ExerciseAttempt.objects.create(
                session=session,
                exercise=exercise,
                user_answer=user_answer,
                is_correct=is_correct,
                time_taken=time_taken
            )
            
            # Actualizar sesión
            if is_correct:
                session.correct_answers += 1
                session.save()
                messages.success(request, "¡Respuesta correcta!")
            else:
                messages.error(request, f"Respuesta incorrecta. La respuesta correcta es {exercise_data['answer']}.")
            
            # Actualizar contador de ejercicios
            exercises_remaining -= 1
            request.session['exercises_remaining'] = exercises_remaining
            
            # Actualizar tiempo de inicio para el siguiente ejercicio
            request.session['exercise_start_time'] = time.time()
            
            return redirect('exercise_solve')
    else:
        form = ExerciseAnswerForm()
        # Actualizar tiempo de inicio
        request.session['exercise_start_time'] = time.time()
    
    context = {
        'form': form,
        'exercise': exercise,
        'session': session,
        'exercises_remaining': exercises_remaining,
        'progress_percentage': int((session.total_exercises - exercises_remaining) / session.total_exercises * 100)
    }
    
    return render(request, 'exercises/solve.html', context)

@login_required
def exercise_results(request, session_id):
    """Vista para mostrar resultados de una sesión de ejercicios"""
    session = get_object_or_404(ExerciseSession, id=session_id, user=request.user)
    attempts = session.attempts.all().order_by('created_at')
    
    # Calcular estadísticas
    stats = {
        'total_exercises': session.total_exercises,
        'correct_answers': session.correct_answers,
        'accuracy': session.accuracy(),
        'duration': session.duration(),
        'avg_time_per_exercise': session.duration() / session.total_exercises if session.total_exercises > 0 else 0,
    }
    
    # Estadísticas por tipo de operación
    operation_stats = {}
    for op_type, op_name in Exercise.OPERATION_CHOICES:
        op_attempts = attempts.filter(exercise__operation_type=op_type)
        op_correct = op_attempts.filter(is_correct=True).count()
        op_total = op_attempts.count()
        
        if op_total > 0:
            operation_stats[op_type] = {
                'name': op_name,
                'total': op_total,
                'correct': op_correct,
                'accuracy': round((op_correct / op_total) * 100, 2)
            }
    
    context = {
        'session': session,
        'attempts': attempts,
        'stats': stats,
        'operation_stats': operation_stats
    }
    
    return render(request, 'exercises/results.html', context)

@login_required
def exercise_history(request):
    """Vista para mostrar historial de sesiones de ejercicios"""
    sessions = ExerciseSession.objects.filter(user=request.user).order_by('-start_time')
    
    # Estadísticas generales
    total_exercises = sessions.aggregate(Sum('total_exercises'))['total_exercises__sum'] or 0
    total_correct = sessions.aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
    
    overall_accuracy = round((total_correct / total_exercises) * 100, 2) if total_exercises > 0 else 0
    
    context = {
        'sessions': sessions,
        'total_exercises': total_exercises,
        'total_correct': total_correct,
        'overall_accuracy': overall_accuracy
    }
    
    return render(request, 'exercises/history.html', context)