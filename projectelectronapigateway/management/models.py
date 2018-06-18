from django.db import models

# Create your models here.


class apiURL(models.Model):
    url1 = models.CharField(max_length=100)
    url2 = models.CharField(max_length=100)
    url3 = models.CharField(max_length=100)
