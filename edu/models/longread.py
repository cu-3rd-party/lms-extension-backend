from django.db import models


class Longread(models.Model):
    lms_id = models.BigIntegerField()
    course_id = models.BigIntegerField()
    theme_id = models.BigIntegerField()

    # Добавлены и переименованы поля для заголовков
    longread_title = models.CharField(max_length=255, null=True, blank=True)
    theme_title = models.CharField(max_length=255, null=True, blank=True)
    course_title = models.CharField(max_length=255, null=True, blank=True)

    contents = models.FileField(upload_to="longreads")

    def __str__(self):
        return f"{self.longread_title}"

    class Meta:
        db_table = "longreads"
        verbose_name = "Longread"
        verbose_name_plural = "Longreads"
