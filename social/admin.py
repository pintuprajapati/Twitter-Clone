from django.contrib import admin
from .models import Post, Comment

# Register your models here.

# Post model registration
@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'body', 'created_on', 'author')


# Comment model registration
@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'created_on', 'author', 'post')