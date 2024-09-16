from django.contrib import admin
from .models import Experience
from .models import Perk


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "price",
        "start",
        "end"
    )

    list_filter = (
        "city",
        "price",
        "host",
        "perks",
    )


@admin.register(Perk)
class PerkAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "details",
    )
