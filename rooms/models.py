from django.db import models


class Room(models.Model):

    """ Room Model Definition """

    class RoomKindChoices(models.TextChoices):
        ENTIRE_PLACE = ("entire_place", "Entire Place")
        PRIVATE_ROOM = ("private_room", "Private Room")
        SHARED_ROOM = ("shared_room", "Shared Room")

    country = models.CharField(max_length=50, default="한국")
    city = models.CharField(max_length=80, default="서울")
    price = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    toilets = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(max_length=255)
    pet_friendly = models.BooleanField(default=True)
    kind = models.CharField(
        max_length=20, choices=RoomKindChoices.choices, default=RoomKindChoices.ENTIRE_PLACE)


class Amenity(models.Model):

    """ Amenities Model Definition """

    name = models.CharField(max_length=150)
    description = models.CharField(max_length=255, null=True)
