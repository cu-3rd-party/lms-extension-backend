from ninja import Schema, ModelSchema

from ..models import Longread


class UploadLongreadRequest(Schema):
    course_id: int
    theme_id: int
    longread_id: int
    download_link: str
    course_title: str | None = None
    theme_title: str | None = None
    longread_title: str | None = None

class LongreadConciseOut(ModelSchema):
    class Meta:
        model = Longread
        fields = ['lms_id']
        # fields_optional = '__all__'
