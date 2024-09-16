from django.db import models
from common.models import CommonModel


class Category(CommonModel):

    """ Room or Experience Category Model Definition """

    class CategoryKindChoices(models.TextChoices):
        ROOMS = ("rooms", "Rooms")
        EXPERIENCES = ("experiences", "Experiences")

    name = models.CharField(max_length=80)
    kind = models.CharField(
        max_length=15, choices=CategoryKindChoices.choices, default=CategoryKindChoices.ROOMS)

    def __str__(self):
        return f"{self.kind.title()}: {self.name}"

    class Meta:
        verbose_name_plural = "Categories"
