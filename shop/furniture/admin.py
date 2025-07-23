from django.contrib import admin
from django.utils.html import format_html
from .models import *
from unfold.admin import ModelAdmin

# Register your models here.

class DiscountFilter(admin.SimpleListFilter):
    title = 'Discount'
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return [
            ('>0', 'Yes'),
            ('=0', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '>0':
            return queryset.filter(discount__gt=0)
        if self.value() == '=0':
            return queryset.filter(discount=0)

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['id', 'title', 'products_count']
    list_display_links = ['id', 'title']

    def products_count(self, obj):
        return obj.product_set.all().count()

@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ['id', 'title', 'products_count']
    list_display_links = ['id', 'title']

    def products_count(self, obj):
        return obj.product_set.all().count()

@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ['id', 'title', 'get_color']
    list_editable = ['title']

    def get_color(self, obj):
        return format_html(f'<div style="width:30px; height:30px; background-color: {obj.color};"></div>')

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ['id', 'title']


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    fk_name = 'product'
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    fk_name = 'product'
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fk_name = 'product'
    extra = 1


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductColorInline, ProductSizeInline, ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['id', 'title', 'brand', 'category', 'available',
                    'price', 'discount', 'final_price', 'first_image']
    list_editable = ['price', 'discount', 'available']
    list_display_links = ['id', 'title']
    list_filter = ['category', DiscountFilter]

    def final_price(self, obj):
        disc_price = float(obj.price) - float(obj.price) * obj.discount / 100
        return disc_price

    def first_image(self, obj):
        try:
            image = obj.images.first().image.url
            return format_html(f'<img src="{image}" width="100px">')
        except:
            return '-'