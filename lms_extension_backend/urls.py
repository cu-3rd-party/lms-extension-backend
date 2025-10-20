"""
URL configuration for lms_extension_backend project.

The `urlpatterns` list routes URLs to api. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function api
    1. Add an import:  from my_app import api
    2. Add a URL to urlpatterns:  path('', api.home, name='home')
Class-based api
    1. Add an import:  from other_app.api import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from edu.auth import ActiveUserAuth
from edu.api.auth import router as auth_router
from edu.api.ping import router as ping_router

api = NinjaAPI(auth=ActiveUserAuth())
api.add_router("", "edu.urls.router")
api.add_router("auth/", auth_router, auth=None)
api.add_router("ping/", ping_router, auth=None)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
