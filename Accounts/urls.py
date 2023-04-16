from django.urls import path
from .views import activate_code, add_instagram, index, login_view, register_view, logout_view, change_password_view, reset_password_view, reset_password_check_view, reset_password_complete_view


urlpatterns = [
    path("", index, name="index"),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('activate_account/<slug>/', activate_code, name='activate_account'),
    path('change_password/', change_password_view, name='change_password'),
    path('reset_password/', reset_password_view, name='reset_password'),
    path('reset_password_check/<uuid64>/<token>/', reset_password_check_view, name='reset_password_check'),
    path('reset_password_complete/<uuid64>/', reset_password_complete_view, name='reset_password_complete'),

    path('add_instagram/', add_instagram, name='add_instagram'),
]
