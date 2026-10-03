from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView

from .forms import *
from .models import *


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')


class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class HomeView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductDeletView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)


class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'cart.html'
    context_object_name = 'items'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = 0
        for item in context['items']:
            total += item.total
        context['total'] = total
        return context


class CartAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if product.quantity <= 0:
            messages.error(request, 'Tovara net v nalichii!')
            return redirect('cart')
        item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1},
        )
        if not created:
            if item.quantity < product.quantity:
                item.quantity += 1
                item.save()
            else:
                messages.error(request, 'Bolwe etogo tovara net na sklade!')
        return redirect('cart')


class CartRemoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(CartItem,pk=pk,user=request.user,)
        item.delete()
        return redirect('cart')

class OrderCreateView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request):
        form = OrderForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'Prover zapolnenie Poley!')
            return redirect('cart')

        if form.cleaned_data['delivery_date'] < timezone.localdate():
            messages.error(request, 'Data dostavki ne mojet bit v prowlom!')
            return redirect('cart')

        items = list(
            CartItem.objects.select_for_update().filter(user=request.user).order_by('product_id')
        )

        if not items:
            messages.error(request, 'Korzina pustaya!')
            return redirect('cart')

        for item in items:
            item.product = get_object_or_404(
                Product.objects.select_for_update(),
                pk=item.product_id,
            )

            if item.quantity > item.product.quantity:
                messages.error(
                    request,
                    f'Nedostatochno tovara : {item.product.name}',
                )
                return redirect('cart')
        order = form.save(commit=False)
        order.user = request.user
        order.save()

        for item in items:
            OrderItems.objects.create(order=order,products=item.product,name=item.product.name,price=item.product.price,quantity=item.quantity,)
            item.product.quantity -= item.quantity
            item.product.save()
            item.delete()
        return redirect('orders')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user,).order_by('-created_at')