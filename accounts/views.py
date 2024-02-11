from django.shortcuts import render, redirect
from django.forms.models import inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *
from .decorators import *

################################################################################
################################################################################
@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # add new user to 'customer' Group
            group = Group.objects.get(name='customer')
            user.groups.add(group)

            # add new user to Customer table
            Customer.objects.create(user=user)

            # display msg for user [display in login page]
            messages.success(request, 'Account was created')
            return redirect('login')
        
            # OR Use Signals -> go to 'signals.py' and 'apps.py' fiels
            # messages.success(request, 'Account was created')
            # return redirect('login')
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def login_page(request):
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

"""
# OR
def login_page(request):
    if request.user.is_authenticated:
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
"""

@login_required(login_url='login')
def logout_page(request):
    logout(request)
    context = {
    }
    return render(request, 'accounts/login.html', context)

################################################################################
################################################################################

@login_required(login_url='login')
@allowed_users(allowd_roles=['customer'])
def user_page(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    panding = orders.filter(status='Panding').count()
    out_for_delivery = orders.filter(status='Out for delivery').count()
    delivred = orders.filter(status='Delivered').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'panding': panding,
        'out_for_delivery': out_for_delivery,
        'delivred': delivred,
    }
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowd_roles=['customer'])
def account_setting(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
    }
    return render(request, 'accounts/account_setting.html', context)

################################################################################
################################################################################

@login_required(login_url='login')
@admin_only
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
@admin_only
def products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
@admin_only
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
        'my_filter': my_filter,
    }
    return render(request, 'accounts/customer.html', context)

@login_required(login_url='login')
@admin_only
def create_order(request, pk):
    """
    customer = Customer.objects.get(id=pk)
    form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer', pk_test=pk)
    context = {
        'form': form,
    }
    """
    # OR
    customer = Customer.objects.get(id=pk)
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    #formset = OrderFormSet(instance=customer)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('customer', pk_test=pk)
    context = {
        'formset': formset,
    }
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@admin_only
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {
        'form': form,
    }
    return render(request, 'accounts/update_form.html', context)

@login_required(login_url='login')
@admin_only
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'order': order,
    }
    return render(request, 'accounts/delete.html', context)
