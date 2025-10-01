from django.core.files.base import ContentFile
from ninja import Router

import requests

from ..schema import *
from ..schema.longread import UploadLongreadRequest
from ..services import *
from ..models import *

router = Router()

@router.post("course/", response={201: Message, 403: Message})
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
        title=body.title,
        theme_id=body.theme_id,
        course_id=body.course_id,
    )
    longread_obj.contents.save(filename, ContentFile(resp.content))

    return 201, Message(message="Longread uploaded successfully")
