from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from ckeditor.fields import RichTextField
import uuid


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    affiliation = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(default='default.jpg',upload_to='media', blank=True, null=True)
    
    def __str__(self):
        return self.user.email

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    

def create_default_categories(sender, **kwargs):
    if sender.name == 'blog':  # Ensure it runs only for the 'blog' app
        default_categories = ["Other"]
        for category in default_categories:
            Category.objects.get_or_create(name=category)

class Blog(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # ForeignKey to Category
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    # Remove the ManyToMany fields and replace with integer counters

    def __str__(self):
        return self.title

