from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.serializers import CategorySerializer

from .models import Category


class Categories(APIView):
    def get(self, request):
        all_categories = Category.objects.all()
        serializer = CategorySerializer(all_categories, many=True)
        return Response({'ok': True, 'categories': serializer.data})

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            new_category = serializer.save()
            category_serializer = CategorySerializer(new_category).data
            return Response({'ok': True, 'category': category_serializer}, status=status.HTTP_201_CREATED)
        else:
            return Response({'ok': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'ok': False, 'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response({'ok': True, 'category': serializer.data})

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            updated_category = serializer.save()
            category_serializer = CategorySerializer(updated_category).data
            return Response({'ok': True, 'category': category_serializer})
        else:
            return Response({'ok': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response({'ok': True}, status=status.HTTP_204_NO_CONTENT)


category_detail = CategoryDetail.as_view()
categories = Categories.as_view()
