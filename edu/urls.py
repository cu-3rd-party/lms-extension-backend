# edu/urls.py
from ninja import Router

# Импортируем роутеры для конкретных функций
from .api.longread import router as longread_router
from .api.ping import router as ping_router

# Создаем главный роутер для приложения "edu"
router = Router()

# Добавляем в него другие роутеры.
# Префиксы будут складываться: /api/ + /ping/ и /api/ + /upload/ и т.д.
#router.add_router("ping/", ping_router)
router.add_router("", longread_router) # У longread_router нет своего префикса

# urlpatterns больше не нужен, так как мы работаем с экземпляром Router