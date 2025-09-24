def verify_download_link(link: str | None) -> bool:
    if not link:
        return False
    return link.startswith("https://storage.yandexcloud.net/university-lms-materials/longreads")
