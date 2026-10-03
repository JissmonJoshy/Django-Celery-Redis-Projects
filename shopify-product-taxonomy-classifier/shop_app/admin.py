from django.contrib import admin
from .models import Product, ProductImage, Category, ClassificationResult, Attribute, ProductAttributeValue


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_number", "product_name", "product_category", "product_sub_category", "msrp")
    search_fields = ("product_number", "product_name", "description")
    list_filter = ("product_category", "product_sub_category")
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "position", "image_url", "is_valid")




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("full_path", "parent")
    search_fields = ("name", "full_path")




@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = ("product", "predicted_category", "confidence", "status", "is_low_confidence")
    list_filter = ("status", "is_low_confidence", "predicted_category")
    search_fields = ("product__product_number", "product__product_name")



@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("result", "attribute", "value", "confidence")
    list_filter = ("attribute",)