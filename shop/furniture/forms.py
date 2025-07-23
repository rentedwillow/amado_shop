from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class AddToCartForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=ProductSize.objects.none(),
        widget=forms.HiddenInput(),  # Скрываем стандартный выпадающий список
    )
    color = forms.ModelChoiceField(
        queryset=ProductColor.objects.none(),
        widget=forms.HiddenInput(),  # Скрываем стандартный выпадающий список
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'id': 'quantity',
                'name': 'quantity',
                'class': 'form-control input-number text-center p-2 mx-1',
                'value': '1'
            }
        )
    )
    def __init__(self, product, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].queryset = ProductSize.objects.filter(product=product)
        self.fields['color'].queryset = ProductColor.objects.filter(product=product)
        self.fields['quantity'].widget.attrs['data-stock'] = product.in_stock


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': 'Password'
    }))


class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': "Your full name"

    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': "Your email address"

    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': "Set your password"

    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3 p-4',
        'placeholder': "Retype your password"

    }))


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['country', 'address', 'city', 'state', 'zipcode', 'phone']
        widgets = {
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country / Region *'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address *'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Town / City *'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State *'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zip Code *'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone *'
            }),
        }