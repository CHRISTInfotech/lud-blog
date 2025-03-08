from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class blog_request(models.Model):
    name = models.CharField(null=False,blank=False,max_length=225)
    mail = models.EmailField(null=False,blank=False)
    status = models.BooleanField(default=True)


class Invitation(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)  # Store the invitation message
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def check_status(self):
        return User.objects.filter(email=self.email).exists()

    def save(self, *args, **kwargs):
        self.accepted = self.check_status()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email} - {'Accepted' if self.accepted else 'Pending'}"
