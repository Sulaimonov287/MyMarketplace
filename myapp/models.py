from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField( max_length=150)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField( max_length=100)
    description = models.TextField()
    price = models.DecimalField( max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.ImageField( upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'product'], name='unique_user_cart_product',),
                       models.CheckConstraint(condition=models.Q(quantity__gte = 1), name='cart_quantity_positive')]

    @property
    def total(self):
        return self.product.price * self.quantity


    def __str__(self):
        return f"{self.user} : {self.product} : {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=300, blank=True)
    delivery_date = models.DateField(null=True, blank=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    products = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def total(self):
        return self.price * self.quantity
  
    def __str__(self):
        return self.name