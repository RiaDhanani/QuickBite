from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, CartItems
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .decorators import *
from django.db.models import Sum

class MenuListView(ListView):
    model = Item
    template_name = 'main/home.html'
    context_object_name = 'menu_items'

class MenuDetailView(DetailView):
    model = Item
    template_name = 'main/dishes.html'

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['title', 'image', 'description', 'price', 'pieces', 'instructions', 'labels', 'label_colour', 'slug']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['title', 'image', 'description', 'price', 'pieces', 'instructions', 'labels', 'label_colour', 'slug']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.created_by:
            return True
        return False

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    success_url = '/item_list'

    def test_func(self):
        item = self.get_object()
        if self.request.user == item.created_by:
            return True
        return False

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    cart_item = CartItems.objects.create(
        item=item,
        user=request.user,
        ordered=False,
    )
    messages.info(request, "Added to Cart!!Continue Shopping!!")
    return redirect("main:cart")

@login_required
def get_cart_items(request):
    cart_items = CartItems.objects.filter(user=request.user,ordered=False)
    bill = cart_items.aggregate(Sum('item__price'))
    number = cart_items.aggregate(Sum('quantity'))
    pieces = cart_items.aggregate(Sum('item__pieces'))
    total = bill.get("item__price__sum")
    count = number.get("quantity__sum")
    total_pieces = pieces.get("item__pieces__sum")
    context = {
        'cart_items':cart_items,
        'total': total,
        'count': count,
        'total_pieces': total_pieces
    }
    return render(request, 'main/cart.html', context)

class CartDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CartItems
    success_url = '/cart'

    def test_func(self):
        cart = self.get_object()
        if self.request.user == cart.user:
            return True
        return False

@login_required
def order_item(request):
    cart_items = CartItems.objects.filter(user=request.user,ordered=False)
    ordered_date=timezone.now()
    cart_items.update(ordered=True,ordered_date=ordered_date)
    messages.info(request, "Item Ordered")
    return redirect("main:order_details")

@login_required
def order_details(request):
    items = CartItems.objects.filter(ordered=True,status="Active").order_by('-ordered_date')
    cart_items = CartItems.objects.filter(ordered=True,status="Delivered").order_by('-ordered_date')
    bill = items.aggregate(Sum('item__price'))
    number = items.aggregate(Sum('quantity'))
    pieces = items.aggregate(Sum('item__pieces'))
    total = bill.get("item__price__sum")
    count = number.get("quantity__sum")
    total_pieces = pieces.get("item__pieces__sum")
    context = {
        'items':items,
        'cart_items':cart_items,
        'total': total,
        'count': count,
        'total_pieces': total_pieces
    }
    return render(request, 'main/order_details.html', context)

@login_required(login_url='/accounts/login/')
@admin_required
def admin_view(request):
    cart_items = CartItems.objects.filter(ordered=True,status="Delivered").order_by('-ordered_date')
    context = {
        'cart_items':cart_items,
    }
    return render(request, 'main/admin_view.html', context)

@login_required(login_url='/accounts/login/')
@admin_required
def item_list(request):
    items = Item.objects.filter(created_by=request.user)
    context = {
        'items':items
    }
    return render(request, 'main/item_list.html', context)
"""
@login_required(login_url='/accounts/login/')
@admin_required
def add_item(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = AddForm()
    form = AddForm()
    items = Item.objects.all()
    context = {
        'form' : form,
        'items' : items,
    }
    return render(request, 'main/add_item.html', context)
"""

@login_required(login_url='/accounts/login/')
@admin_required
def pending_orders(request):
    items = CartItems.objects.filter(ordered=True,status="Active").order_by('-ordered_date')
    context = {
        'items':items,
    }
    return render(request, 'main/pending_orders.html', context)

@login_required(login_url='/accounts/login/')
@admin_required
def admin_dashboard(request):
    cart_items = CartItems.objects.filter(ordered=True)
    pending_total = CartItems.objects.filter(ordered=True,status="Active").count()
    completed_total = CartItems.objects.filter(ordered=True,status="Delivered").count()
    count1 = CartItems.objects.filter(ordered=True,item="6").count()
    count2 = CartItems.objects.filter(ordered=True,item="7").count()
    count3 = CartItems.objects.filter(ordered=True,item="8").count()
    total = CartItems.objects.filter(ordered=True).aggregate(Sum('item__price'))
    income = total.get("item__price__sum")
    context = {
        'pending_total' : pending_total,
        'completed_total' : completed_total,
        'income' : income,
        'count1' : count1,
        'count2' : count2,
        'count3' : count3,
    }
    return render(request, 'main/admin_dashboard.html', context)

