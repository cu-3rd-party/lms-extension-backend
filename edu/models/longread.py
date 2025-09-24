from django.contrib.auth.models import User
from django.db import models
from . import *


class Longread(models.Model):
    _id = models.BigIntegerField()
    title = models.CharField(max_length=255)
    parent_theme = models.ForeignKey(Theme, models.CASCADE)
    parent_course = models.ForeignKey(Course, models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'longreads'
        verbose_name = 'Longread'
        verbose_name_plural = "Longreads"
