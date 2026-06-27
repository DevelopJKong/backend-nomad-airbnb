from django.shortcuts import get_object_or_404

from .models import Amenity, Room
from .schemas import AmenityIn


def list_rooms():
    # depth=1 중첩 직렬화의 N+1 방지: FK는 select_related, M2M는 prefetch_related
    return Room.objects.select_related('owner', 'category').prefetch_related('amenities').all()


def get_room(room_id: int) -> Room:
    return Room.objects.select_related('owner', 'category').prefetch_related('amenities').get(pk=room_id)


def list_amenities():
    return Amenity.objects.all()


def create_amenity(payload: AmenityIn) -> Amenity:
    return Amenity.objects.create(**payload.dict())


def get_amenity(amenity_id: int) -> Amenity:
    return get_object_or_404(Amenity, pk=amenity_id)


def update_amenity(amenity_id: int, payload: AmenityIn) -> Amenity:
    amenity: Amenity = get_object_or_404(Amenity, pk=amenity_id)

    # setattr 사용
    # for attr, value in payload.dict().items():
    # setattr(amenity, attr, value)

    amenity.name = payload.name
    amenity.description = payload.description
    amenity.save()
    return amenity


def delete_amenity(amenity_id: int) -> None:
    amenity: Amenity = get_object_or_404(Amenity, pk=amenity_id)
    amenity.delete()
