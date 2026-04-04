from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from categories.views import router as categories_router

api = NinjaAPI(version='1.0.0')
api.add_router('/categories/', categories_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/rooms/', include('rooms.urls')),
    path('api/v1/', api.urls),
]
