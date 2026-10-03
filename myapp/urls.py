from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('products/', HomeView.as_view(), name='products'),
    path('products/add/', ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/delete/', ProductDeletView.as_view(), name='product_delete'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:pk>/', CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<int:pk>/', CartRemoteView.as_view(), name='cart_remove'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrderListView.as_view(), name='orders'),
]