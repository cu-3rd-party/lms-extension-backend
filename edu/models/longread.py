from django.db import models


class Longread(models.Model):
    lms_id = models.BigIntegerField()
    title = models.CharField(max_length=255)
    theme_id = models.BigIntegerField()
    course_id = models.BigIntegerField()
    contents = models.FileField(upload_to='longreads')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'longreads'
        verbose_name = 'Longread'
        verbose_name_plural = "Longreads"
