from django import forms
from django.contrib.auth.models import User
from .models import *
from django.utils import timezone

class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)


    class Meta:
        model = User
        fields = ['username', 'email', 'password']


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'quantity', 'image']
        labels = {'category':'Category'}

        def clean_price(self):
            price = self.cleaned_data['price']

            if price <= 0:
                raise forms.ValidationError('Sena doljna bit bolshe 0!')

            return price

        def clean_quantity(self):
            quantity = self.cleaned_data['quantity']

            if quantity < 0:
                raise forms.ValidationError('Kolichestvo products doljen bit bolwe 0!')
            return quantity


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'delivery_date', 'description']
