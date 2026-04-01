from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import Response

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
            print(serializer.validated_data)
            return Response({'ok': True, 'category': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'ok': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view()
def category(request, pk):
    category = Category.objects.get(pk=pk)
    serializer = CategorySerializer(category)
    return Response({'ok': True, 'category': serializer.data})
