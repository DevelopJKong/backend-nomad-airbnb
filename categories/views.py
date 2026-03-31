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
        return Response({'ok': False, 'error': 'GET method only allowed'})


@api_view()
def category(request, pk):
    category = Category.objects.get(pk=pk)
    serializer = CategorySerializer(category)
    return Response({'ok': True, 'category': serializer.data})
