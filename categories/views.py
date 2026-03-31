from rest_framework.decorators import api_view
from rest_framework.views import Response

from .models import Category


@api_view(['GET'])
def categories(request):
    all_categories = Category.objects.all()
    return Response({'ok': True, 'categories': all_categories})
