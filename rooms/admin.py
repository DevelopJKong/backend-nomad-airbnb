from django.contrib import admin

from .models import Amenity, Room

# Register your models here.


@admin.action(description='Set all prices to zero')
def reset_prices(model_admin, request, rooms):
    for room in rooms:
        room.price = 0
        room.save()


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    actions = (reset_prices,)

    list_display = (
        'name',
        'price',
        'kind',
        'owner',
        'total_amenities',
        'rating',
        'created_at',
    )

    list_filter = (
        'country',
        'city',
        'price',
        'rooms',
        'toilets',
        'pet_friendly',
        'kind',
        'amenities',
    )

    # 아무것도 적어주지 않으면 contains 검색
    # ^ 로 시작하는 검색
    # = 정확히 일치하는 검색
    search_fields = ('name', 'price', 'owner__username')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
