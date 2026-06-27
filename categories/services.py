from django.shortcuts import get_object_or_404

from .models import Category
from .schemas import CategoryIn, CategoryPatch


def list_categories():
    return Category.objects.all()


def create_category(payload: CategoryIn) -> Category:
    return Category.objects.create(**payload.dict())


def get_category(pk: int) -> Category:
    return get_object_or_404(Category, pk=pk)


def update_category(pk: int, payload: CategoryPatch) -> Category:
    category: Category = get_object_or_404(Category, pk=pk)
    category.name = payload.name
    category.kind = payload.kind
    category.save()
    return category


def delete_category(pk: int) -> None:
    category: Category = get_object_or_404(Category, pk=pk)
    category.delete()
