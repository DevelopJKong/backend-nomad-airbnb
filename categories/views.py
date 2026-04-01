from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from categories.serializers import CategorySerializer

from .models import Category


@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'GET':
        all_categories = Category.objects.all()
        serializer = CategorySerializer(all_categories, many=True)
        return Response({'ok': True, 'categories': serializer.data})
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            new_category = serializer.save()
            category_serializer = CategorySerializer(new_category).data
            return Response({'ok': True, 'category': category_serializer}, status=status.HTTP_201_CREATED)
        else:
            return Response({'ok': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'ok': False, 'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response({'ok': True, 'category': serializer.data})
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            category_serializer = CategorySerializer(updated_category).data
            return Response({'ok': True, 'category': category_serializer})
        else:
            return Response({'ok': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response({'ok': True}, status=status.HTTP_204_NO_CONTENT)
