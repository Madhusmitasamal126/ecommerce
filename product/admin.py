from django.contrib import admin
from .models import Category, Product, ProductImage, ColorVariant, SizeVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['cat_name', 'slug']


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['pro_name', 'category', 'price', 'product_desc']
    inlines = [ProductImageAdmin]
    prepopulated_fields = {"slug": ("pro_name",)}


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price']