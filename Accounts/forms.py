from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordChangeForm
from .models import Instagram

User = get_user_model()


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError('Email or Password is wrong')
        
        if not user.is_active:
            raise forms.ValidationError('Your account is not active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Enter your username or email"})
        self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Enter password"})


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password_confirm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"First name"})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Last name"})
        self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Username"})
        self.fields['email'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Email"})
        self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Password"})
        self.fields['password_confirm'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Password confirm"})


    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This user already exists')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This user already exists')

        if len(password) < 6:
            raise forms.ValidationError('Min length is 6')

        if password != password_confirm:
            raise forms.ValidationError("passwords don't match")

        return self.cleaned_data


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(required=True, label='Old Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Your Old Password'
            }))
    new_password1 = forms.CharField(required=True, label='New Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Your New Password'
            }))
    new_password2 = forms.CharField(required=True, label='Confirm New Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Confirm Your New Password'
            }))


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email','username','password1','password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email','username', 'password', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class ResetPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Enter your email"})


    def clean(self):
        email = self.cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This user doesn't exists")

        return self.cleaned_data


class ResetPasswordCompleteView(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="New Password Confirm")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"New Password"})
        self.fields['password_confirm'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"New Password Confirm"})

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if len(password) < 6:
            raise forms.ValidationError('Min length is 6')

        if password != password_confirm:
            raise forms.ValidationError("passwords don't match")

        return self.cleaned_data


class InstagramForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Instagram
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Username"})
        self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder' :"Password"})

