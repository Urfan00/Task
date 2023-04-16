from django.shortcuts import render, redirect, get_object_or_404, reverse
from .forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordCompleteView, ChangePasswordForm, InstagramForm
from .models import Instagram
from selenium import webdriver
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from services.generator import Generator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .decorators import not_authorized_user, check_activation_code_time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from selenium.webdriver.common.by import By
import time
from .tasks import update_instagram_account_info

User = get_user_model()


@not_authorized_user
def login_view(request):
    form = LoginForm()
    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('/')
        else:
            print(form.errors)

    context = {
        'form' : form
    }

    return render(request, 'login.html', context)


def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST or None)

        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data.get('username')
            new_user.email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            new_user.set_password(password)
            new_user.is_active = False
            new_user.activation_code = Generator.create_code_for_activate(size=6, model_=User)
            new_user.activation_code_expires_at = timezone.now() + timezone.timedelta(minutes=2)
            new_user.save()

            # send mail part
            send_mail(
                "Activation Code",
                f"Your activation code : {new_user.activation_code}",
                settings.EMAIL_HOST_USER ,
                [new_user.email]
            )

            # login(request, new_user)
            return redirect('activate_account', slug=new_user.slug)
        else:
            print(form.errors)
        
    context = {
        'form' : form
    }

    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('/login/')

@check_activation_code_time
def activate_code(request, slug):
    user  = get_object_or_404(User, slug=slug)
    context = {}

    if request.method == 'POST':
        code = request.POST.get('code')
        if code == user.activation_code:
            user.is_active = True
            user.activation_code = None
            user.activation_code_expires_at = None
            user.save()

            login(request, user)
            return redirect('/')
        
    return render(request, 'activate.html', context)


@login_required(login_url='/')
def change_password_view(request):
    form = ChangePasswordForm(user=request.user)

    if request.method == 'POST':
        form = ChangePasswordForm(data = request.POST or None, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

            return redirect('/')

    context = {
        'form' : form
    }
    return render(request, 'change_password.html', context)


def reset_password_view(request):
    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email = email)

            # mail process

            uuid64 = urlsafe_base64_encode(force_bytes(user.id))
            print(f"UUIDE64: {uuid64}")

            token = PasswordResetTokenGenerator().make_token(user)
            print(f"TOKEN: {token}")

            link = request.build_absolute_uri(reverse(
                'reset_password_check',
                kwargs={
                    'uuid64': uuid64,
                    'token': token
                }
                ))
            # send mail
            send_mail(
                'RESET PASSWORD',
                f"Please click the link below\n{link}",
                settings.EMAIL_HOST_USER,
                [email]
            )

            return redirect('/login/')
        else:
            print(form.errors)

    context = {
        'form' : form
    }

    return render(request, 'reset_password.html', context)


def reset_password_check_view(request, uuid64, token):
    id = force_str(urlsafe_base64_decode(uuid64))
    user = User.objects.get(id=id)

    if not PasswordResetTokenGenerator().check_token(user=user, token=token):
        messages.error(request, 'Token is wrong')
        return redirect('/login/')
    return redirect('reset_password_complete', uuid64=uuid64)


def reset_password_complete_view(request, uuid64):
    form = ResetPasswordCompleteView()
    id = force_str(urlsafe_base64_decode(uuid64))
    user = User.objects.get(id=id)

    if request.method == "POST":
        form = ResetPasswordCompleteView(request.POST or None)

        if form.is_valid():
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            return redirect('/login/')

    context = {
        'form': form
    }

    return render(request, 'reset_password_complete.html', context)


@login_required(login_url='/login/')
def index(request):
    # update_instagram_account_info.delay()
    instagrams = Instagram.objects.filter(user=request.user).all()
    context = {
        'instagrams': instagrams,
    }
    return render(request, 'index.html', context)


@login_required(login_url='/login/')
def add_instagram(request):
    form = InstagramForm()
    if request.method == 'POST':
        form = InstagramForm(request.POST or None)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            driver = webdriver.Chrome()
            driver.get('https://www.instagram.com/')
            driver.implicitly_wait(5)

            username_input = driver.find_element('name', 'username')
            password_input = driver.find_element('name', 'password')
            username_input.send_keys(username)
            password_input.send_keys(password)

            login_button = driver.find_element("css selector",'#loginForm > div > div:nth-child(3) > button > div')
            login_button.click()
            driver.implicitly_wait(5)
            time.sleep(3)

            driver.get("https://www.instagram.com/" + username)
            # driver.implicitly_wait(5)
            time.sleep(5)

            try:
                followers = driver.find_element("css selector", '.x78zum5 li:nth-child(2) button span')
                following = driver.find_element("css selector", '.x78zum5 li:nth-child(3) button span')
            except:
                followers = driver.find_element("xpath", '//a[contains(@href,"/followers")]/span')
                following = driver.find_element("xpath", '//a[contains(@href,"/following")]/span')

            follower_count = followers.text
            following_count = following.text
            driver.quit()

            instagram = Instagram(username=username, password=password, following=int(following_count), follower=int(follower_count), user=request.user)
            instagram.save()
        return redirect('/')
    context = {
        'form': form,
    }

    return render(request, 'add_instagram.html', context)

