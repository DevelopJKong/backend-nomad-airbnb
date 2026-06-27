from django.shortcuts import get_object_or_404

from .models import Amenity
from .schemas import AmenityIn


def list_amenities():
    return Amenity.objects.all()


def create_amenity(payload: AmenityIn) -> Amenity:
    return Amenity.objects.create(**payload.dict())


def get_amenity(amenity_id: int) -> Amenity:
    return get_object_or_404(Amenity, pk=amenity_id)


def update_amenity(amenity_id: int, payload: AmenityIn) -> Amenity:
    amenity = get_object_or_404(Amenity, pk=amenity_id)
    for attr, value in payload.dict().items():
        setattr(amenity, attr, value)
    amenity.save()
    return amenity


def delete_amenity(amenity_id: int) -> None:
    amenity = get_object_or_404(Amenity, pk=amenity_id)
    amenity.delete()
