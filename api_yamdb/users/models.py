from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class CustomAccountManager(BaseUserManager):

    def create_user(self, email, username, password, **other_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('role', 'admin')

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, username, password, **other_fields)


class User(AbstractUser):
    USER_ROLE = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )

    username = models.CharField(
        ('Логин'),
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, '
                   'digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    email = models.EmailField('Email адрес', max_length=254, unique=True,
                              blank=False)
    password = models.CharField('Пароль', max_length=128, blank=True)
    role = models.CharField('Роль', max_length=16, choices=USER_ROLE,
                            default='user')
    confirmation_code = models.IntegerField('Код подтверждения', blank=True,
                                            null=True)
    bio = models.TextField('Биогрфия пользователя', max_length=512, blank=True)

    objects = CustomAccountManager()

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username
