from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg
from datetime import timedelta, datetime
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile, Progress, ActivityLog

def register_view(request):
    """Vista para el registro de usuarios"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear registro de actividad
            ActivityLog.objects.create(
                user=user,
                activity_type='registro',
                description='Usuario registrado en el sistema'
            )
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """Vista para el inicio de sesión"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Crear registro de actividad
                ActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    description='Inicio de sesión exitoso'
                )
                messages.success(request, f'¡Bienvenido, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    # Crear registro de actividad
    ActivityLog.objects.create(
        user=request.user,
        activity_type='logout',
        description='Cierre de sesión'
    )
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Vista para el dashboard del usuario"""
    user = request.user
    progress = Progress.objects.get(user=user)
    
    # Obtener estadísticas de rendimiento
    stats = {
        'total_exercises': progress.total_exercises,
        'correct_answers': progress.correct_answers,
        'accuracy': progress.accuracy_percentage(),
        'addition_accuracy': progress.operation_accuracy('addition'),
        'subtraction_accuracy': progress.operation_accuracy('subtraction'),
        'multiplication_accuracy': progress.operation_accuracy('multiplication'),
        'division_accuracy': progress.operation_accuracy('division'),
    }
    
    # Obtener actividad reciente
    recent_activity = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
    
    context = {
        'user': user,
        'profile': user.profile,
        'progress': progress,
        'stats': stats,
        'recent_activity': recent_activity,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile_view(request):
    """Vista para ver y actualizar el perfil del usuario"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Crear registro de actividad
            ActivityLog.objects.create(
                user=request.user,
                activity_type='actualización_perfil',
                description='Perfil actualizado'
            )
            messages.success(request, '¡Tu perfil ha sido actualizado!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)

@login_required
def progress_view(request):
    """Vista para ver el progreso detallado del usuario"""
    user = request.user
    progress = Progress.objects.get(user=user)
    
    # Estadísticas por tipo de operación
    operation_stats = {
        'addition': {
            'total': progress.addition_exercises,
            'correct': progress.addition_correct,
            'accuracy': progress.operation_accuracy('addition')
        },
        'subtraction': {
            'total': progress.subtraction_exercises,
            'correct': progress.subtraction_correct,
            'accuracy': progress.operation_accuracy('subtraction')
        },
        'multiplication': {
            'total': progress.multiplication_exercises,
            'correct': progress.multiplication_correct,
            'accuracy': progress.operation_accuracy('multiplication')
        },
        'division': {
            'total': progress.division_exercises,
            'correct': progress.division_correct,
            'accuracy': progress.operation_accuracy('division')
        }
    }
    
    context = {
        'progress': progress,
        'operation_stats': operation_stats,
    }
    return render(request, 'users/progress.html', context)

@login_required
def activity_log_view(request):
    """Vista para ver el historial de actividad del usuario"""
    user = request.user
    logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')
    
    context = {
        'logs': logs,
    }
    return render(request, 'users/activity_log.html', context)