from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
########ADMIN#########
#username: admin
#password: admin

class Login(AbstractUser):
    usertype=models.CharField(max_length=50)
    viewpassword=models.CharField(max_length=50)

class Reviewer(models.Model):
    login = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to='reviewers/', null=True, blank=True)



class Product(models.Model):
    """
    One row = one product from Product_List.xlsx.
    """
    product_number = models.CharField(max_length=100, unique=True)
    model_number = models.CharField(max_length=100, blank=True)

    product_category = models.CharField(max_length=200, blank=True)       # supplier's category, NOT Shopify's
    product_sub_category = models.CharField(max_length=200, blank=True)
    collection_name = models.CharField(max_length=200, blank=True)
    color_collection = models.CharField(max_length=200, blank=True)
    product_color = models.CharField(max_length=200, blank=True)

    product_name = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    bullets = models.TextField(blank=True)
    set_includes = models.TextField(blank=True)

    product_weight = models.CharField(max_length=100, blank=True)
    materials = models.CharField(max_length=300, blank=True)
    product_dimensions = models.TextField(blank=True)
    assembly_required = models.CharField(max_length=10, blank=True)
    is_a_set = models.CharField(max_length=10, blank=True)
    stackable = models.CharField(max_length=10, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)

    item_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    map_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    msrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    shipping_method = models.CharField(max_length=100, blank=True)
    total_box_count = models.IntegerField(null=True, blank=True)
    pallet_count = models.IntegerField(null=True, blank=True)
    shipping_weight = models.CharField(max_length=100, blank=True)
    total_cbm = models.CharField(max_length=100, blank=True)
    package_dimensions = models.TextField(blank=True)

    product_url = models.URLField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_number} - {self.product_name}"


class ProductImage(models.Model):
    """
    A product can have up to 20 image URLs (Image 1..Image 20 in the Excel).
    Each one gets its own row here instead of 20 separate columns.
    """
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)
    position = models.PositiveSmallIntegerField(default=1)
    is_valid = models.BooleanField(null=True, blank=True)  # None = not checked yet

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.product_number} - image {self.position}"



class Category(models.Model):
    """
    A small slice of Shopify's real taxonomy tree, scoped to what our
    products actually need (furniture + lighting). Self-referencing
    so it can represent parent > child hierarchy.
    """
    name = models.CharField(max_length=200)               # e.g. "Sofas & Couches"
    full_path = models.CharField(max_length=500, unique=True)  # e.g. "Home & Garden > Furniture > Living Room Furniture > Sofas & Couches"
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    description = models.TextField(blank=True)  # used by the matching logic - keywords/description text

    def __str__(self):
        return self.full_path



import json

class ClassificationResult(models.Model):
    STATUS_CHOICES = [
        ('needs_review', 'Needs Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='classification')
    predicted_category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    confidence = models.FloatField(default=0.0)
    alternatives_json = models.TextField(blank=True)  # JSON list of runner-up categories + scores
    is_low_confidence = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='needs_review')
    notes = models.TextField(blank=True)  # why it failed, if it did

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_alternatives(self):
        return json.loads(self.alternatives_json) if self.alternatives_json else []

    def __str__(self):
        return f"{self.product.product_number} -> {self.predicted_category} ({self.confidence:.2f})"





class Attribute(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. "Color", "Material"

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    result = models.ForeignKey(ClassificationResult, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    confidence = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.result.product.product_number} - {self.attribute.name}: {self.value}"