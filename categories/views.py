from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Category
from .schemas import CategoryIn, CategoryOut, CategoryPatch

router = Router()


@router.get('/', response=list[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@router.post('/', response={201: CategoryOut})
def create_category(request, payload: CategoryIn):
    category = Category.objects.create(**payload.dict())
    return 201, category


@router.get('/{pk}', response=CategoryOut)
def get_category(request, pk: int):
    return get_object_or_404(Category, pk=pk)


@router.put('/{pk}', response=CategoryOut)
def update_category(request, pk: int, payload: CategoryPatch):
    category = get_object_or_404(Category, pk=pk)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    category.save()
    return category


@router.delete('/{pk}', response={204: None})
def delete_category(request, pk: int):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return 204, None
