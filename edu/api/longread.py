from django.core.files.base import ContentFile
from ninja import Router

import requests

from ..schema import *
from ..schema.longread import UploadLongreadRequest, LongreadConciseOut, LongreadIDOut
from ..services import *
from ..models import *

router = Router()


@router.post("course/", response={201: Message, 403: Message, 500: Message})
def upload_longread_api(request, body: UploadLongreadRequest):
    if not verify_download_link(body.download_link):
        return 403, Message(message="You have provided invalid download link")

    resp = requests.get(body.download_link, timeout=20)
    if resp.status_code != 200:
        return 500, Message(message="Failed to download file from the provided link")

    # longread_obj.contents = downloaded_data
    filename = f"{body.longread_id}.pdf"
    longread_obj = Longread(
        lms_id=body.longread_id,
        title=body.longread_title,
        theme_id=body.theme_id,
        course_id=body.course_id,
    )
    longread_obj.contents.save(filename, ContentFile(resp.content))

    return 201, Message(message="Longread uploaded successfully")


@router.get("course/{course_id}/theme/{theme_id}/longread/{longread_id}/", response={200: BaseFile, 404: NotFoundError})
def full_get_longread_api(request, course_id: int, theme_id: int, longread_id: int):
    longread_obj = Longread.objects.filter(
        course_id=course_id,
        theme_id=theme_id,
        lms_id=longread_id
    )
    if not longread_obj.exists():
        return 404, NotFoundError()
    longread_obj = longread_obj.first()
    with longread_obj.contents.open("r") as contents:
        data = contents.read()

    return 200, BaseFile(contents=data)

@router.get("course/{course_id}/", response={200: list[LongreadConciseOut], 404: NotFoundError})
def get_course(request, course_id: int):
    longreads = Longread.objects.filter(
        course_id=course_id,
    )
    if not longreads.exists():
        return 404, NotFoundError()

    return 200, [LongreadConciseOut(
                    longread_id=i.lms_id,
                    theme_id=i.theme_id,
                    course_id=i.course_id,
        ) for i in longreads.all()]

@router.get("course/{course_id}/theme/{theme_id}/", response={200: list[LongreadIDOut], 404: NotFoundError})
def get_theme(request, course_id: int, theme_id: int):
    longreads = Longread.objects.filter(
        course_id=course_id,
        theme_id=theme_id,
    )
    if not longreads.exists():
        return 404, NotFoundError()

    return 200, [LongreadIDOut(id=i.lms_id) for i in longreads.all()]
