import requests
import base64
from django.core.files.base import ContentFile
from django.db import transaction
from ninja import Router
# --- ИЗМЕНЕНИЕ ЗДЕСЬ: Добавлен недостающий импорт ---
from django.core.files.temp import NamedTemporaryFile

from ..models import Longread, LongreadFile
from ..schema import *
from ..schema.longread import (
    UploadLongreadRequest,
    LongreadConciseOut,
    LongreadIDOut,
    FetchLongreadsRequest,
    MissingLongreads,
)
from ..services import *


router = Router()


def verify_download_link(link: str | None) -> bool:
    """
    Проверяет, что ссылка для скачивания начинается с доверенного домена.
    """
    if not link:
        return False
    return link.startswith(
        "https://storage.yandexcloud.net/university-lms-materials/"
    )


@router.post("upload/", response={201: Message, 200: Message, 403: Message, 500: Message})
@transaction.atomic
def upload_longread(request, body: UploadLongreadRequest):
    """
    Загружает новый лонгрид или обновляет метаданные существующего.
    """
    longread_obj, created = Longread.objects.get_or_create(
        lms_id=body.longread_id,
        course_id=body.course_id,
        theme_id=body.theme_id,
        defaults={
            "longread_title": body.longread_title,
            "theme_title": body.theme_title,
            "course_title": body.course_title,
        },
    )

    if not created:
        # Лонгрид уже существовал. Обновляем его названия на случай, если они изменились.
        longread_obj.longread_title = body.longread_title
        longread_obj.theme_title = body.theme_title
        longread_obj.course_title = body.course_title
        longread_obj.save()
        
        # Немедленно выходим из функции. Цикл загрузки файлов не будет выполнен.
        return 200, Message(message="Longread metadata updated. Files were not changed.")

    # Этот код выполнится только если лонгрид был новым (created == True)
    for file_info in body.files:
        if not verify_download_link(file_info.download_link):
            return 403, Message(
                message=f"Invalid download link provided: {file_info.download_link}"
            )

        try:
            with requests.get(file_info.download_link, timeout=180, stream=True) as resp:
                resp.raise_for_status()

                with NamedTemporaryFile(delete=True) as temp_file:
                    for chunk in resp.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_file.flush()

                    longread_file = LongreadFile(
                        longread=longread_obj, original_filename=file_info.filename
                    )
                    longread_file.file.save(file_info.filename, temp_file)

        except requests.RequestException as e:
            transaction.set_rollback(True)
            return 500, Message(
                message=f"Failed to download file from {file_info.download_link}: {e}"
            )

    return 201, Message(
        message="New longread with all files uploaded successfully"
    )


@router.get(
    "course/{course_id}/theme/{theme_id}/longread/{longread_id}/",
    response={200: list[BaseFile], 404: NotFoundError},
)
def get_longread_contents(
    request, course_id: int, theme_id: int, longread_id: int
):
    try:
        longread_obj = Longread.objects.prefetch_related("files").get(
            course_id=course_id, theme_id=theme_id, lms_id=longread_id
        )
    except Longread.DoesNotExist:
        return 404, NotFoundError()

    if not longread_obj.files.exists():
        return 200, []

    response_files = []
    for longread_file in longread_obj.files.all():
        with longread_file.file.open("rb") as f:
            data_bytes = f.read()

        encoded_data = base64.b64encode(data_bytes).decode("ascii")
        response_files.append(
            BaseFile(
                filename=longread_file.original_filename, contents=encoded_data
            )
        )

    return 200, response_files


@router.get("courses/", response={200: list[LongreadConciseOut]})
def get_available_info(request):
    longreads = Longread.objects.all()
    return 200, [
        LongreadConciseOut(
            longread_id=i.lms_id,
            theme_id=i.theme_id,
            course_id=i.course_id,
            longread_title=i.longread_title,
            theme_title=i.theme_title,
            course_title=i.course_title,
        )
        for i in longreads
    ]


@router.get(
    "course/{course_id}/",
    response={200: list[LongreadConciseOut], 404: NotFoundError},
)
def get_course(request, course_id: int):
    longreads = Longread.objects.filter(
        course_id=course_id,
    )
    if not longreads.exists():
        return 404, NotFoundError()
    return 200, [
        LongreadConciseOut(
            longread_id=i.lms_id,
            theme_id=i.theme_id,
            course_id=i.course_id,
            longread_title=i.longread_title,
            theme_title=i.theme_title,
            course_title=i.course_title,
        )
        for i in longreads
    ]


@router.get(
    "course/{course_id}/theme/{theme_id}/",
    response={200: list[LongreadIDOut], 404: NotFoundError},
)
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