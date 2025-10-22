from ninja import Router
from django.http import HttpResponse

router = Router()


@router.get("/readme", url_name="readme")
def readme(request):
    html_content = """
    ну шо, а вот и README
    https://github.com/cu-3rd-party/

    <h1>html поддерживает<h1>
    
    <br><br>
    биба и боба

    """
    return HttpResponse(html_content, content_type="text/html")