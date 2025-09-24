from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    _id = models.IntegerField()
    title = models.CharField(max_length=511)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = "Courses"
