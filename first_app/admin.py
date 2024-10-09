from django.contrib import admin
# Register your models here.
from first_app.models import Book, Publisher, Author # Post
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from .models.book import CustomUser


admin.site.register(CustomUser)
admin.site.unregister(Group)
admin.site.register(Group)
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(Author)
#admin.site.register(Post)
