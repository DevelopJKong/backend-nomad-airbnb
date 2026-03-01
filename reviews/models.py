from django.db import models

from common.models import CommonModel

# Create your models here.


class Review(CommonModel):
    """Review Model Definition"""

    payload = models.TextField()
    rating = models.PositiveIntegerField()
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, blank=True)
    experience = models.ForeignKey('experiences.Experience', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.room} / {self.rating}'
