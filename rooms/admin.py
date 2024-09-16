from django.contrib import admin
from .models import Room
from .models import Amenity

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass
