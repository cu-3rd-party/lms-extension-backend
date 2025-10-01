from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from ninja import Router

import requests

from ..services import *
from ..models import *

router = Router()

@api_view(['POST'])
def upload(request: Request):
    """
    В запросе обязательно:
    id курса
    id темы
    id лонгрида
    ссылка на скачивание материала

    Опционально:
    Название курса
    Название темы
    Название лонгрида
    """
    course_id = request.POST.get('course_id')
    if not course_id: return Response(status=status.HTTP_400_BAD_REQUEST)
    theme_id = request.POST.get('theme_id')
    if not theme_id: return Response(status=status.HTTP_400_BAD_REQUEST)
    longread_id = request.POST.get('longread_id')
    if not longread_id: return Response(status=status.HTTP_400_BAD_REQUEST)
    download_link = request.POST.get('download_link')
    if not download_link or not verify_download_link(download_link): return Response(status=status.HTTP_400_BAD_REQUEST)

    course_title = request.POST.get('course_title') if request.POST.get('course_title') else ""
    theme_title = request.POST.get('theme_title') if request.POST.get('theme_title') else ""
    longread_title = request.POST.get('longread_title') if request.POST.get('longread_title') else ""

    course_obj = filter_or_create(Course, course_id, course_title)
    theme_obj = filter_or_create(Theme, theme_id, theme_title)
    theme_obj.parent_course = course_obj
    longread_obj = filter_or_create(Longread, longread_id, longread_title)
    longread_obj.parent_theme = theme_obj
    longread_obj.parent_course = course_obj

    downloaded_data = requests.get(download_link, timeout=20)
    longread_obj.contents = downloaded_data

    return Response({
        'message': 'you have used upload endpoint',
    }, status.HTTP_200_OK)
