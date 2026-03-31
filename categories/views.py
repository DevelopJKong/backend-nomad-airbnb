from rest_framework.decorators import api_view
from rest_framework.views import Response

from categories.serializers import CategorySerializer

from .models import Category


@api_view(['GET'])
def categories(request):
    all_categories = Category.objects.all()
    serializer = CategorySerializer(all_categories, many=True)
    return Response({'ok': True, 'categories': serializer.data})
