from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from categories.views import router as categories_router
from rooms.views import router as amenities_router

api = NinjaAPI(
    version='1.0.0',
    title='Airbnb Clone API',
    description='노마드코더 에어비앤비 클론 백엔드 API 문서입니다.\n\n'
    'Swagger UI: `/api/v1/docs` · OpenAPI 스키마: `/api/v1/openapi.json`',
    docs_url='/docs',
)
api.add_router('/categories/', categories_router, tags=['Categories'])
api.add_router('/amenities/', amenities_router, tags=['Amenities'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
