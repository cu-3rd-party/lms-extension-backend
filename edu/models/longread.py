from django.db import models


class Course(models.Model):
    """
    Модель для хранения информации о курсе.
    """
    lms_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = "Courses"


class Theme(models.Model):
    """
    Модель для хранения информации о теме внутри курса.
    """
    lms_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='themes')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'themes'
        verbose_name = 'Theme'
        verbose_name_plural = "Themes"


class Longread(models.Model):
    """
    Модель для лонгрида. Теперь связана с моделями Theme и Course.
    """
    lms_id = models.BigIntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='longreads')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='longreads')
    contents = models.FileField(upload_to='longreads')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'longreads'
        verbose_name = 'Longread'
        verbose_name_plural = "Longreads"