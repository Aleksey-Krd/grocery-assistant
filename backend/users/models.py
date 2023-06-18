from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

ANONYMOUS = 'anonymous'
USER = 'user'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):

    username_validator = AbstractUser.username_validator

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Требуется. 150 символов или меньше. Буквы, цифры и @/./+/-/_'),
        validators=[username_validator],
        error_messages={
            'unique': _("Пользователь с таким именем пользователя существует"),
        },
    )
    first_name = models.CharField(
        verbose_name='Имя', 
        max_length=150, 
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        blank=False,
        unique=True
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=30,
        default=USER
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_anonymous_user(self):
        return self.role == ANONYMOUS

    @property
    def is_authenticated_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    def save(self, *args, **kwargs):
        if self.is_superuser or self.role == ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)
