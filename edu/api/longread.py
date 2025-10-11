import requests
from django.core.files.base import ContentFile
from ninja import Router
import base64
from ..models import Longread, Course, Theme  # Импортируем новые модели
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

    # Создаем или обновляем курс с его заголовком
    course_obj, _ = Course.objects.update_or_create(
        lms_id=body.course_id,
        defaults={'title': body.course_title}
    )

    # Создаем или обновляем тему с ее заголовком
    theme_obj, _ = Theme.objects.update_or_create(
        lms_id=body.theme_id,
        course=course_obj,
        defaults={'title': body.theme_title}
    )

    # Создаем или обновляем лонгрид
    longread_obj, _ = Longread.objects.update_or_create(
        lms_id=body.longread_id,
        theme=theme_obj,
        course=course_obj,
        defaults={'title': body.longread_title}
    )

    filename = f"{body.longread_id}.pdf"
    longread_obj.contents.save(filename, ContentFile(resp.content), save=True)

    return 201, Message(message="Longread uploaded successfully")


@router.get("course/{course_id}/theme/{theme_id}/longread/{longread_id}/", response={200: BaseFile, 404: NotFoundError})
def get_longread_contents(request, course_id: int, theme_id: int, longread_id: int):
    # Фильтрация по course_id и theme_id будет работать как и раньше
    longread_obj = Longread.objects.filter(
        course_id=course_id,
        theme_id=theme_id,
        lms_id=longread_id
    ).first()

    if not longread_obj:
        return 404, NotFoundError()

    with longread_obj.contents.open("rb") as contents:
        binary_data = contents.read()
        base64_encoded_data = base64.b64encode(binary_data).decode('utf-8')

    return 200, BaseFile(contents=base64_encoded_data, filename=longread_obj.contents.name)


@router.get("courses/", response={200: list[LongreadConciseOut]})
def get_available_info(request):
    # Используем select_related для оптимизации запроса и получения связанных данных
    longreads = Longread.objects.select_related('theme', 'course').all()
    return 200, [LongreadConciseOut(
        longread_id=i.lms_id,
        longread_title=i.title,
        theme_id=i.theme_id,
        theme_title=i.theme.title,
        course_id=i.course_id,
        course_title=i.course.title,
    ) for i in longreads]


@router.get("course/{course_id}/", response={200: list[LongreadConciseOut], 404: NotFoundError})
def get_course(request, course_id: int):
    longreads = Longread.objects.filter(
        course_id=course_id,
    ).select_related('theme', 'course')
    if not longreads.exists():
        return 404, NotFoundError()

    return 200, [LongreadConciseOut(
        longread_id=i.lms_id,
        longread_title=i.title,
        theme_id=i.theme_id,
        theme_title=i.theme.title,
        course_id=i.course_id,
        course_title=i.course.title,
    ) for i in longreads]


@router.get("course/{course_id}/theme/{theme_id}/", response={200: list[LongreadIDOut], 404: NotFoundError})
def get_theme(request, course_id: int, theme_id: int):
    longreads = Longread.objects.filter(
        course_id=course_id,
        theme_id=theme_id,
    )
    if not longreads.exists():
        return 404, NotFoundError()

    return 200, [LongreadIDOut(id=i.lms_id, title=i.title) for i in longreads]


@router.post("fetch/", response={200: MissingLongreads})
def fetch_longreads(request, body: FetchLongreadsRequest):
    triples = []
    for course in body.courses:
        for theme in course.themes:
            for longread_id in theme.longreads:
                triples.append((course.course_id, theme.theme_id, longread_id))

    if not triples:
        return 200, MissingLongreads(missing_longreads=[])

    # Этот код продолжает работать без изменений благодаря ForeignKey
    existing = set(
        Longread.objects.filter(
            course_id__in=[c for c, _, _ in triples],
            theme_id__in=[t for _, t, _ in triples],
            lms_id__in=[l for _, _, l in triples],
        ).values_list("course_id", "theme_id", "lms_id")
    )

    missing = [l for (c, t, l) in triples if (c, t, l) not in existing]

    return 200, MissingLongreads(missing_longreads=missing)