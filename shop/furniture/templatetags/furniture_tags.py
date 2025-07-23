from django import template
from furniture.models import Category, Brand, WishList
# from furniture.utils import CartForAuthenticatedUser

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()

@register.simple_tag()
def get_brands():
    return Brand.objects.all()

@register.simple_tag()
def get_sorters():
    return [
        ('title', 'Name (A - Z)'),
        ('-title', 'Name (Z - A)'),
        ('price', 'Price (Low-High)'),
        ('-price', 'Price (High-Low)'),
    ]

@register.simple_tag()
def query_transform(request, key, value):
    updated = request.GET.copy()
    updated[key] = value
    return updated.urlencode()

@register.simple_tag()
def check_wishlist(request, pk):
    return WishList.objects.filter(product_id=pk, user=request.user).exists()