from .models import Product, Cart, CartProduct

class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None, color=None, size=None, quantity=1):
        self.user = request.user

        if product_id and action:
            self.add_or_delete(product_id, action, color, size, quantity)

    def get_cart_info(self):
        cart, created = Cart.objects.get_or_create(user=self.user)
        cart_products = cart.cartproduct_set.all()

        cart_total_price = cart.get_cart_total_price
        cart_total_quantity =cart.get_cart_total_quantity

        return {
            'cart': cart,
            'products': cart_products,
            'cart_total_price': cart_total_price,
            'cart_total_quantity': cart_total_quantity
        }

    def add_or_delete(self, product_id, action, color, size, quantity):
        cart = self.get_cart_info()['cart']
        product = Product.objects.get(pk=product_id)

        cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product,
                                                                  size=size, color=color)
        if action == 'add' and product.in_stock > quantity:
            cart_product.quantity += int(quantity)
            product.in_stock -= int(quantity)
        elif action == 'delete':
            cart_product.quantity -= int(quantity)
            product.in_stock += int(quantity)

        product.save()
        cart_product.save()

        if cart_product.quantity <= 0:
            cart_product.delete()


    def clear(self):
        cart = self.get_cart_info()['cart']
        cart_products = cart.cartproduct_set.all()
        for product in cart_products:
            product.delete()
        cart.save()