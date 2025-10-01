from django.urls import path
from .api import *
from ninja import Router

router = Router()
router.add_router("ping/", ping_router)
router.add_router("upload/", upload_router)

urlpatterns = [
    # path("ping/", ping, name="ping"),
    # path("upload/", upload, name="upload"),
]
