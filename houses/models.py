from django.db import models


class House(models.Model):

    """Model Definition for Houses"""

    name = models.CharField(max_length=140)
    price = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(max_length=140)
    pets_allowed = models.BooleanField(
        verbose_name="Pets allowed?",
        default=True, help_text="Is pet allowed?")
    owner = models.ForeignKey(
        "users.User", related_name="houses", on_delete=models.CASCADE
    )


def __str__(self):
    return self.name
