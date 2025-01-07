import sys

from django.db import models
from django.contrib.auth.models import BaseUserManager ,AbstractBaseUser ,PermissionsMixin
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self ,email , password , **extra_kwargs):
        if not email:
            raise ValueError('email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email , **extra_kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self ,email , password , **extra_kwargs):
        extra_kwargs.setdefault('is_superuser' ,True)
        extra_kwargs.setdefault('is_staff' ,True)
        extra_kwargs.setdefault('is_active' ,True)
        extra_kwargs.setdefault('is_verified' ,True)

        if extra_kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser')

        if extra_kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(email , password , **extra_kwargs)

class User(AbstractBaseUser ,PermissionsMixin):
    email = models.EmailField(null=False , blank=False ,unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'

    objects= UserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField('User' , on_delete=models.CASCADE ,related_name='profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateTimeField(null=True ,blank=True)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
