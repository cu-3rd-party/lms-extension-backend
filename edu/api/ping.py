from ninja import Router

from ..schema import Message

router = Router()


@router.get("/", url_name="ping", response={200: Message})
def ping(request):
    return 200, Message(message="hello")
