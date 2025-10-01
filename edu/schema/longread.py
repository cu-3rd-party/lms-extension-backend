from ninja import Schema


class UploadLongreadRequest(Schema):
    course_id: int
    theme_id: int
    longread_id: int
    download_link: str
    course_title: str | None = None
    theme_title: str | None = None
    longread_title: str | None = None
