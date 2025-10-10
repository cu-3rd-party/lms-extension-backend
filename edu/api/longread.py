import requests
from django.core.files.base import ContentFile
from ninja import Router
import base64
from ..models import *
from ..schema import *
from ..schema.longread import UploadLongreadRequest, LongreadConciseOut, LongreadIDOut, FetchLongreadsRequest, \
    MissingLongreads
from ..services import *

router = Router()


@router.post("upload/", response={201: Message, 403: Message, 500: Message})
def upload_longread(request, body: UploadLongreadRequest):
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
def get_longread_contents(request, course_id: int, theme_id: int, longread_id: int):
    longread_obj = Longread.objects.filter(
        course_id=course_id,
        theme_id=theme_id,
        lms_id=longread_id
    ).first()

    if not longread_obj:
        return 404, NotFoundError()

    with longread_obj.contents.open("rb") as contents: # Open in binary read mode
        binary_data = contents.read()
        # Encode binary data to a Base64 string to safely include in JSON
        base64_encoded_data = base64.b64encode(binary_data).decode('utf-8')

    return 200, BaseFile(contents=base64_encoded_data, filename=longread_obj.contents.name)


@router.get("courses/", response={200: list[LongreadConciseOut]})
def get_available_info(request):
    longreads = Longread.objects.all()
    return 200, [LongreadConciseOut(
        longread_id=i.lms_id,
        theme_id=i.theme_id,
        course_id=i.course_id,
    ) for i in longreads.all()]


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


@router.post("fetch/", response={200: MissingLongreads})
def fetch_longreads(request, body: FetchLongreadsRequest):
    triples = []
    for course in body.courses:
        for theme in course.themes:
            for longread_id in theme.longreads:
                triples.append((course.course_id, theme.theme_id, longread_id))

    if not triples:
        return 200, {"missing_longreads": []}

    existing = set(
        Longread.objects.filter(
            course_id__in=[c for c, _, _ in triples],
            theme_id__in=[t for _, t, _ in triples],
            lms_id__in=[l for _, _, l in triples],
        ).values_list("course_id", "theme_id", "lms_id")
    )

    missing = [l for (c, t, l) in triples if (c, t, l) not in existing]

    return 200, {"missing_longreads": missing}
