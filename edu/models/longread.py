from django.db import models
import os

class Longread(models.Model):
    lms_id = models.BigIntegerField()
    course_id = models.BigIntegerField()
    theme_id = models.BigIntegerField()

    longread_title = models.CharField(max_length=255, null=True, blank=True)
    theme_title = models.CharField(max_length=255, null=True, blank=True)
    course_title = models.CharField(max_length=255, null=True, blank=True)
    
    # Поле contents убрано. Теперь Longread - это просто группирующая сущность.

    def __str__(self):
        return f"{self.longread_title}"

    class Meta:
        db_table = "longreads"
        verbose_name = "Longread"
        verbose_name_plural = "Longreads"

# Функция для генерации пути сохранения файлов
def get_upload_path(instance, filename):
    # Файлы будут храниться в /media/longreads/course_<id>/theme_<id>/longread_<id>/<filename>
    return os.path.join(
        "longreads",
        f"course_{instance.longread.course_id}",
        f"theme_{instance.longread.theme_id}",
        f"longread_{instance.longread.lms_id}",
        filename,
    )

class LongreadFile(models.Model):
    # Связь с "контейнером"-лонгридом. 
    # related_name='files' позволит обращаться к файлам через longread.files.all()
    # on_delete=models.CASCADE означает, что при удалении лонгрида удалятся все связанные с ним файлы.
    longread = models.ForeignKey(Longread, related_name='files', on_delete=models.CASCADE)
    
    # Поле для хранения самого файла
    file = models.FileField(upload_to=get_upload_path)
    
    # Сохраняем оригинальное имя файла для удобства
    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return f"File {self.original_filename} for {self.longread.longread_title}"

    class Meta:
        db_table = "longread_files"
        verbose_name = "Longread File"
        verbose_name_plural = "Longread Files"
