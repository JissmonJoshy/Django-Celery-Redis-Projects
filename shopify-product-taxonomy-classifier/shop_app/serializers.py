from rest_framework import serializers
from .models import Product, Category, ClassificationResult, ProductAttributeValue


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'full_path']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_number', 'product_name', 'description', 'product_category', 'product_sub_category']


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['attribute_name', 'value', 'confidence']


class ClassificationResultSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    predicted_category = CategorySerializer(read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)
    alternatives = serializers.SerializerMethodField()

    class Meta:
        model = ClassificationResult
        fields = ['id', 'product', 'predicted_category', 'confidence', 'is_low_confidence',
                  'status', 'notes', 'alternatives', 'attribute_values']

    def get_alternatives(self, obj):
        return obj.get_alternatives()