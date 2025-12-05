from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

ROLE_HIERARCHY = {
    'admin': 4,
    'medico': 3,
    'atendente': 2,
    'paciente': 1,
}

def get_user_role(user):
    if user.is_superuser or user.is_staff:
        return 'admin'
    try:
        return user.perfil.tipo_usuario
    except:
        return 'paciente'

def get_role_level(role):
    return ROLE_HIERARCHY.get(role, 0)

def role_required(*allowed_roles, redirect_url='home'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Faça login para acessar esta página.')
                return redirect('login')
            
            user_role = get_user_role(request.user)
            
            if user_role in allowed_roles or user_role == 'admin':
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect(redirect_url)
        return wrapper
    return decorator

def min_role_required(min_role, redirect_url='home'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Faça login para acessar esta página.')
                return redirect('login')
            
            user_role = get_user_role(request.user)
            user_level = get_role_level(user_role)
            required_level = get_role_level(min_role)
            
            if user_level >= required_level:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect(redirect_url)
        return wrapper
    return decorator

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta página.')
            return redirect('login')
        
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        try:
            if request.user.perfil.tipo_usuario == 'admin':
                return view_func(request, *args, **kwargs)
        except:
            pass
        
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('home')
    return wrapper

def medico_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta página.')
            return redirect('login')
        
        user_role = get_user_role(request.user)
        
        if user_role in ['admin', 'medico']:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso restrito a médicos.')
        return redirect('home')
    return wrapper

def atendente_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta página.')
            return redirect('login')
        
        user_role = get_user_role(request.user)
        
        if user_role in ['admin', 'medico', 'atendente']:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso restrito a funcionários.')
        return redirect('home')
    return wrapper

def paciente_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para acessar esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
