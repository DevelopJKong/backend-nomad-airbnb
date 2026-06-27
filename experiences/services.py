from django.shortcuts import get_object_or_404

from .models import Perk
from .schemas import PerkIn


def list_perks():
    return Perk.objects.all()


def create_perk(payload: PerkIn) -> Perk:
    return Perk.objects.create(**payload.dict())


def get_perk(perk_id: int) -> Perk:
    return get_object_or_404(Perk, pk=perk_id)


def update_perk(perk_id: int, payload: PerkIn) -> Perk:
    perk: Perk = get_object_or_404(Perk, pk=perk_id)
    perk.name = payload.name
    perk.explanation = payload.explanation
    perk.details = payload.details
    perk.save()
    return perk


def delete_perk(perk_id: int) -> None:
    perk: Perk = get_object_or_404(Perk, pk=perk_id)
    perk.delete()
