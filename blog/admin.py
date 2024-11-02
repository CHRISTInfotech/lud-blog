from django.contrib import admin
from .models import Post, Comment, Category

# Register your models here.


class PostModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_created')

admin.site.register(Post, PostModelAdmin)
admin.site.register(Comment)
admin.site.register(Category)


