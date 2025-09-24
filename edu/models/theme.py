from django.contrib.auth.models import User
from django.db import models
from . import *


class Theme(models.Model):
    _id = models.IntegerField()
    parent_course = models.ForeignKey(Course, models.CASCADE)
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'themes'
        verbose_name = 'Theme'
        verbose_name_plural = "Themes"
