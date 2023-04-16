from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# class EmailOrUsernameModelBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(email=username)
#         except UserModel.DoesNotExist:
#             try:
#                 user = UserModel.objects.get(username=username)
#             except UserModel.DoesNotExist:
#                 return None
#         if user.check_password(password):
#             return user


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if '@' in username:
                validate_email(username)
                user = UserModel.objects.get(email=username)
            else:
                user = UserModel.objects.get(username=username)
        except (UserModel.DoesNotExist, ValidationError):
            return None
        if user.check_password(password):
            return user