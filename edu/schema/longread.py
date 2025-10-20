from ninja import Schema

# Новая схема для описания одного файла при загрузке
class FileLink(Schema):
    download_link: str
    filename: str

class UploadLongreadRequest(Schema):
    course_id: int
    theme_id: int
    longread_id: int
    # Теперь принимаем список файлов для загрузки
    files: list[FileLink]
    course_title: str | None = None
    theme_title: str | None = None
    longread_title: str | None = None


class LongreadIDOut(Schema):
    id: int


class LongreadConciseOut(Schema):
    longread_id: int
    theme_id: int
    course_id: int
    longread_title: str | None = None
    theme_title: str | None = None
    course_title: str | None = None


class ThemeOverview(Schema):
    theme_id: int
    longreads: list[int]


class CourseOverview(Schema):
    course_id: int
    themes: list[ThemeOverview]


class FetchLongreadsRequest(Schema):
    courses: list[CourseOverview]


class MissingLongreads(Schema):
    missing_longreads: list[int]