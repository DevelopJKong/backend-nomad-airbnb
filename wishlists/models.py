from django.db import models
from common.models import CommonModel

# Create your models here.


class Wishlist(CommonModel):
    """ WishList Model Definition """
    name = models.CharField(max_length=150)
    wishlists = models.PositiveIntegerField()
    rooms = models.ManyToManyField(
        "rooms.Room", related_name="wishlists", blank=True)

    experiences = models.ManyToManyField(
        "experiences.Experience", related_name="wishlists", blank=True)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
