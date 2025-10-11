from ninja import Schema


class UploadLongreadRequest(Schema):
    course_id: int
    theme_id: int
    longread_id: int
    download_link: str
    course_title: str | None = None
    theme_title: str | None = None
    longread_title: str | None = None


class LongreadIDOut(Schema):
    id: int
    title: str | None = None


class LongreadConciseOut(Schema):
    longread_id: int
    longread_title: str | None = None
    theme_id: int
    theme_title: str | None = None
    course_id: int
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