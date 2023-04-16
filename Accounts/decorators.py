from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def not_authorized_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def check_activation_code_time(view_func):
    def wrapper_func(request, *args, **kwargs):
        user = get_object_or_404(User, slug = kwargs.get('slug'))
        now = timezone.now()

        if now > user.activation_code_expires_at:
            return redirect('/')
        else:
            return view_func(request, *args, **kwargs) 
    return wrapper_func
