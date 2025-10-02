from ninja import Router

from .api import *

router = Router()
router.add_router("ping/", ping_router)
router.add_router("/", upload_router)

urlpatterns = [
    # path("ping/", ping, name="ping"),
    # path("upload/", upload, name="upload"),
]
