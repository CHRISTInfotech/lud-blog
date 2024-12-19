from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class blog_request(models.Model):
    name = models.CharField(null=False,blank=False,max_length=225)
    mail = models.EmailField(null=False,blank=False)
    status = models.BooleanField(default=True)
