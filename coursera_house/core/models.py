from django.db import models

class Setting(models.Model):
    """  Model that writes value of controller """
    controller_name = models.CharField(max_length=40, unique=True)
    value = models.IntegerField(default=20)