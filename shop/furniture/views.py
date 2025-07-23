from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.db.models import ExpressionWrapper, F, FloatField
from django.core.paginator import Paginator

from .forms import LoginForm, RegisterForm, AddToCartForm, ShippingAddressForm
from .models import *
from django.urls import reverse
from .utils import CartForAuthenticatedUser

# Create your views here.

def index(request):
    products = Product.objects.order_by('-sales')[:9]
    context = {
        'products': products,
        'title': 'Главная страница'
    }
    return render(request, 'furniture/index.html', context)


class ProductFilter:
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset

    def filter_by_category(self):
        category = self.request.GET.get('category')
        if category:
            self.queryset = self.queryset.filter(category__id=category)
        return self

    def filter_by_brand(self):
        brand = self.request.GET.get('brand')
        if brand:
            self.queryset = self.queryset.filter(brand__id=brand)
        return self

    def sort_by(self):
        sort = self.request.GET.get('sort')
        if sort:
            self.queryset = self.queryset.order_by(sort)
        return self

    def paginate(self):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.queryset, 9)
        return paginator.get_page(page)

    def filter_by_price(self):
        price = self.request.GET.get('price')

        self.queryset = self.queryset.annotate(
            discount_price=ExpressionWrapper(
                F('price') - F('price') * F('discount') / 100.0,
                output_field=FloatField()
            )
        )

        if price:
            if price == '0_50':
                self.queryset = self.queryset.filter(discount_price__lt=50)
            elif price == '50_100':
                self.queryset = self.queryset.filter(discount_price__gte=50, discount_price__lt=100)
            elif price == '100_250':
                self.queryset = self.queryset.filter(discount_price__gte=100, discount_price__lt=250)
            elif price == '250_500':
                self.queryset = self.queryset.filter(discount_price__gte=250, discount_price__lt=500)
            elif price == '500_1000':
                self.queryset = self.queryset.filter(discount_price__gte=500, discount_price__lt=1000)
            elif price == '1000_5000':
                self.queryset = self.queryset.filter(discount_price__gte=1000, discount_price__lt=5000)
            elif price == 'more_5000':
                self.queryset = self.queryset.filter(discount_price__gt=5000)

        return self


    def get_queryset(self):
        return self.queryset


def shop_view(request):
    products = Product.objects.all()
    product_filter = ProductFilter(request, products)
    products = (product_filter
                .filter_by_category()
                .filter_by_brand()
                .filter_by_price()
                .sort_by()
                .get_queryset())
    paginated_products = product_filter.paginate()
    context = {
        'products': paginated_products
    }
    return render(request, 'furniture/shop.html', context)

def product_details(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        form = AddToCartForm(product)
        context = {
            'form': form,
            'product': product,
        }
        return render(request, 'furniture/product-details.html', context)
    except Exception as e:
        print(e)
        return render(request, 'furniture/error.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():  # Все ли данные соответствуют типам
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('index')
            else:
                return redirect('account')
        else:
            return redirect('account')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('account')
        else:
            return redirect('account')


def logout_view(request):
    logout(request)
    return redirect('index')


def account(request):
    context = {
        'login_form': LoginForm(),
        'register_form': RegisterForm()
    }
    return render(request, 'furniture/account.html', context)


def wishlist_action(request, pk):
    product = Product.objects.get(pk=pk)
    user = request.user
    if WishList.objects.filter(product=product, user=user).exists():
        wish = WishList.objects.get(product=product, user=user)
        wish.delete()
    else:
        WishList.objects.create(product=product, user=user)
    return redirect(request.META.get('HTTP_REFERER'))


def favourite(request):
    user = request.user
    favourites = WishList.objects.filter(user=user)
    products = [i.product for i in favourites]
    context = {
        'products': products,
        'title': 'Избранное'
    }
    return render(request, 'furniture/favourite.html', context)

def to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = AddToCartForm(data=request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity', 1)
            color = form.cleaned_data.get('color', None)
            if color:
                color = color.color.title
            else:
                color = 'No'
            size = form.cleaned_data.get('size', None)
            if size:
                size = size.size.title
            else:
                size = 'No'
            CartForAuthenticatedUser(request, product_id, 'add', color, size, quantity)
        else:
            print(form.errors)
    return redirect('product', product.slug)


def plus_minus(request, pk, action, color, size, quantity):
    if request.user.is_authenticated:
        CartForAuthenticatedUser(request, pk, action, color, size, quantity)
        return redirect('cart')


def cart(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)

        cart_info = user_cart.get_cart_info()
        print(cart_info)
        cart_info['title'] = 'Моя корзина'
        return render(request, 'furniture/cart.html', cart_info)


def clear(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        user_cart.clear()
        return redirect('cart')


def checkout(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        context = {
            'shipping_form': ShippingAddressForm(),
            'title': 'Оформление заказа',
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'cart_total_price': cart_info['cart_total_price'],
            'order': cart_info['cart'],
            'products': cart_info['products']
        }
        return render(request, 'furniture/checkout.html', context)


def process_checkout(request):
    if request.method == 'POST':
        shipping_form = ShippingAddressForm(data=request.POST)
        if shipping_form.is_valid():
            ship_address = shipping_form.save(commit=False)
            ship_address.user = request.user
            ship_address.save()
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        cart_products = cart_info['products']
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': cart_product.product.title
                },
                'unit_amount': int(cart_product.product.get_discount_price() * 100)
            },
            'quantity': cart_product.quantity
        } for cart_product in cart_products]
        import stripe
        STRIPE_PUBLISH_KEY = 'pk_test_51QKiwRLmn1k8TixhUfjJlSdYeDsJwizeyDzSfHvTkf8PrZE4Cop1mTK3Yp0upOHScajycmSOlkk2G1isag2tPw7e00mflidk2T'
        STRIPE_SECRET_KEY = 'sk_test_51QKiwRLmn1k8Tixh5Ryz6yd5yBAcod4MngFlGMTPkX9eABit3TksFGFPi8RquTHKxcEJQmJbhfoU68A0YGSGrrIu001nkR0JmY'
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout')),
        )
        return redirect(session.url, 303)


def success_payment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    return render(request, 'furniture/thank_you.html')