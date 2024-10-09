from django.db import models
from django.db.models import UniqueConstraint, Q
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _

from first_app.managers import SoftDeleteManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    birth_date = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'birth_date']

    def __str__(self):
        return self.username


# class Post(models.Model):
#     title = models.CharField(max_length= 170)
#     content =models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.title


class Genre(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)


class Publisher(models.Model):
    name = models.CharField(max_length=75)
    established_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=40, null=True)
    published_date = models.DateField(verbose_name='publication_date')
    registered = models.BooleanField(null=True)
    managed = models.BooleanField(null=True)
    page_count = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    discounted_price = models.IntegerField(null=True)
    publisher = models.ForeignKey(Publisher, null=True, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genre, blank=True, related_name='books')
    is_banned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Поле для мягкого удаления

    objects = SoftDeleteManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.title} написано {self.author}"

    class Meta:
        db_table = 'Book'
        ordering = ['published_date']
        get_latest_by = 'published_date'
        unique_together = ('title', 'author')
        indexes = [models.Index(fields=('title', 'author'), name='title_auth_index')]

        constraints = [UniqueConstraint(fields=['title'], condition=Q(registered=True), name='unique_title_registered'
                                        )
                       ]
        verbose_name = 'fiction book'  # Человекочитаемое имя модели
        verbose_name_plural = 'fiction books'  # Человекочитаемое множественное число имени модели
