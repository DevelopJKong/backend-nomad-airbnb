from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=50)
    kind = serializers.ChoiceField(required=True, choices=Category.CategoryKindChoices.choices)

    class Meta:
        model = Category
        fields = ('pk', 'name', 'kind', 'created_at')
        read_only_fields = ('pk', 'created_at')

    def validate_kind(self, value):
        if value not in Category.CategoryKindChoices.values:
            raise serializers.ValidationError('"rooms" 또는 "experiences"만 가능합니다.')
        return value
