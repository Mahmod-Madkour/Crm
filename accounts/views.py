from django.shortcuts import render, redirect
from django.forms.models import inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *

def register_page(request):
    if request.user.is_authenticed:
        return redirect('login')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created')
                return redirect('login')
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login_page(request):
    if request.user.is_authenticed:
        return redirect('login')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username Or Password is incorrect')
                return render(request, 'accounts/login.html')
    context = {
    }
    return render(request, 'accounts/login.html', context)

def logout_page(request):
    logout(request)
    context = {
    }
    return render(request, 'accounts/login.html', context)

@login_required(login_url='login')
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_orders = orders.count()

    panding = orders.filter(status='Panding').count()
    out_for_delivery = orders.filter(status='Out for delivery').count()
    delivred = orders.filter(status='Delivered').count()
    
    context = {
        'orders': orders,
        'customers': customers,
        'total_orders': total_orders,
        'panding': panding,
        'out_for_delivery': out_for_delivery,
        'delivred': delivred,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()

    order_count = orders.count()
    
    my_filter = OrderFilter(request.GET, queryset=orders)
    orders = my_filter.qs

    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count,
        'my_filter': my_filter
    }
    return render(request, 'accounts/customer.html', context)

@login_required(login_url='login')
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(instance=customer)
    #formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {
        'formset': formset
    }
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {
        'form': form
    }
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'order': order
    }
    return render(request, 'accounts/delete.html', context)
