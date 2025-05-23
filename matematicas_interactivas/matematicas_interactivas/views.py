from django.shortcuts import redirect

def home(request):
    """Vista para la página principal que redirecciona a login o dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')