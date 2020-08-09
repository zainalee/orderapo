from django.shortcuts import render, redirect
from products.models import *
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
import json
import datetime
# from django.contrib.auth.forms import UserCreationForm
from templates.gui.forms import UserForm, SellerFrom, ProductForm, LoginForm, CLoginForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decoraters import unauthenticated, allowed_users
from profiles.models import SellerProfile
from django.contrib.auth.models import PermissionsMixin

from products.models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.filters import ProductFilter
from django.conf import settings
# from .filters import UserFilter


# def search(request):
#     product_list = Product.objects.all()
#     user_filter = UserFilter(request.GET, queryset=product_list)
#     return render(request, 'gui/product_search.html', {'filter': user_filter})


def main(request):
    products_list = Product.objects.all()
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        orderItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        orderItems = order['get_cart_items']

    filter = ProductFilter(request.GET, queryset=products_list)
    products_list = filter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(products_list, 12)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)
    # context = {
    #     'products_list': products_list,
    #     'product': product,
    #     'page': page
    # }
    return render(request, 'gui/main.html', {'product': product, 'filter': filter, 'orderItems': orderItems})


def detailview(request, pk):
    product_detail = Product.objects.get(id=pk)
    user = Product.objects.filter(user=request.user)
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        orderItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        orderItems = order['get_cart_items']
    print("user ", user)
    context = {
        'product_detail': product_detail,
        'user': user,
        'orderItems': orderItems
    }
    return render(request, 'gui/detailview.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['sellers'])
def home(request):
    # user = User.objects.filter(user=request.user)
    # context = {'user': user}
    product = Product.objects.filter(user=request.user).count()
    product_owner = Product.objects.filter(user=request.user)
    print(product_owner)
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        orderItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        orderItems = order['get_cart_items']
    context = {
        'product': product,
        'orderItems': orderItems
    }
    return render(request, 'gui/home.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['sellers'])
def products(request):
    products = Product.objects.filter(user=request.user)
    context = {'products': products, }
    return render(request, 'sellerprofile/myproducts.html', context)


@unauthenticated
def login(request):
    form = LoginForm
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # user = SellerProfile
        user = authenticate(
            request, username=username, password=password)
        if user is not None:
            # if user.role == "seller_profile":
            auth_login(request, user)
            return redirect('adminhome')
        else:
            messages.error(request, 'Username or password is incorrect!')
    context = {
        'form': form
    }
    return render(request, 'sellerprofile/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('login')


@unauthenticated
def registration(request):
    if request.method == 'POST':
        # username = request.POST.get('first_name')
        # password = request.POST.get('username')
        # username = request.POST.get('password')
        # password = request.POST.get('password2')
        form = UserForm(request.POST)
        sellerFrom = SellerFrom(request.POST)
        if form.is_valid() and sellerFrom.is_valid():
            cnic = form.cleaned_data.get('cnic')
            v = len(str(cnic))
            print(v)
            user = form.save()
            seller = sellerFrom.save()
            seller.user = user
            seller.save()
            username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            gorup = Group.objects.get(name='sellers')
            user.groups.add(gorup)
            messages.success(request, 'account was created for' + username)
            # form = UserForm()
            # sellerFrom = SellerFrom()
            return redirect('login')
    else:
        form = UserForm()
        sellerFrom = SellerFrom()

    context = {'form': form, 'sellerForm': sellerFrom}
    return render(request, 'gui/signup.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['sellers'])
def createproduct(request):
    categories = Categories.objects.all()
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            quantity = form.cleaned_data.get("quantity")
            minorder = form.cleaned_data.get("minorder")
            price = form.cleaned_data.get("price")
            image = form.cleaned_data.get("image")
            title = form.cleaned_data.get("title")
            print(quantity)
            print(price)
            print(minorder)
            print(title)
            # if(quantity >= minorder):
            print("quantity checked")
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('products')
        else:
            messages.error(request, "Please Fill all Fields")
    else:
        form = ProductForm()
    context = {'form': form, 'categories': categories}
    return render(request, 'sellerprofile/creatproduct.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['sellers'])
def updateproduct(request, pk):
    product = Product.objects.get(id=pk)
    # form = ProductForm(request.POST,
    #                    request.FILES,  instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST,
                           request.FILES,  instance=product)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.save()
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    context = {'form': form}
    return render(request, 'sellerprofile/updateproduct.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['sellers'])
def deleteproduct(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    context = {'product': product}
    return render(request, 'gui/deleteproduct.html', context)


# @unauthenticated
# def ClientRegistration(request):
#     form = UserForm()
#     print('welcome to client view')
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         print('method checked')
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             print('form processed')
#             password = form.cleaned_data.get('password1')
#             gorup = Group.objects.get(name='clients')
#             user.groups.add(gorup)
#             messages.success(request, 'account was created for' + username)
#             form = UserForm()
#             return redirect('login')
#     else:
#         form = UserForm()
#     context = {'form': form}
#     return render(request, 'sellerprofile/sregister.html', context)

@unauthenticated
def ClientRegistration(request):
    context = {}
    if request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            # email = form.cleaned_data.get('email')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(email=email, password=raw_password)
            # login(request, account)
            return redirect('login')
        else:
            messages.error(request, "this field require")
            context['form'] = form
    else:
        form = UserForm()
        context['form'] = form
        # return render(request, 'account/register.html', context)
    return render(request, 'sellerprofile/sregister.html', context)


@unauthenticated
def Clientlogin(request):
    form = CLoginForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # user = SellerProfile
        user = authenticate(
            request, username=username, password=password)
        if user is not None:
            # if user.role == "seller_profile":
            auth_login(request, user)
            return redirect('main')
        else:
            messages.info(request, 'Username or password is incorrect')
    context = {'form': form}
    return render(request, 'gui/Clientlogin.html', context)


def cart(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
        orderItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        orderItems = order['get_cart_items']
    context = {
        'items': items,
        'order': order,
        'orderItems': orderItems
    }
    return render(request, 'gui/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    # product_detail = Product.objects.get(id=pk)
    context = {
        'items': items,
        'order': order
    }
    return render(request, "gui/checkout.html", context)


def updateItem(request):
    print("view test")
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action: ', action)
    print('ProductId: ', productId)
    user = request.user

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, complete=False)
    total = order.get_cart_total
    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product, user=user, price=product.get_price)
    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
        # return redirect('cart')
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)

    if action == 'delete':
        order_item.quantity = 0

    order_item.save()
    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse("item was added", safe=False)


# @csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    user = request.user
    usernname = request.user.username
    order, created = Order.objects.get_or_create(user=user, complete=False)
    order.transaction_id = transaction_id
    order.complete = True
    order.save()
    ShippingAddress.objects.create(
        name=usernname,
        user=user,
        order=order,
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zipcode=data['zipcode'],
    )

    # total=float(data[])

    print("transaction id is :", transaction_id)
    print('data:', request.body)
    return JsonResponse("order Completed", safe=False)


def demo(request):
    return render(request, "sellerprofile/layout.html")


def shop(request):
    return render(request, "shop/navbar.html")


def profile(request):
    return render(request, "sellerprofile/profile.html")


def showprofile(request, pk):

    return render(request, "sellerprofile/profile.html")


def myOrders(request):
    order = Order.objects.filter(user=request.user).order_by('-date_orderd')
    orderitems = OrderItem.objects.filter(
        user=request.user).order_by('-date_orderd')
    detail = zip(order, orderitems)
    return render(request, "sellerprofile/myOrders.html", {'detail': detail})


def selling(request):
    order = Order.objects.all()
    items = OrderItem.objects.all()
    # address = ShippingAddress.objects.filter(
    #     user__in=Subquery(order.values('id')))
    uid = request.user.id
    # # orderitems = OrderItem.objects.filter(product.user == request.user.id)
    # orderitems = OrderItem.objects.select_related('product', 'order')

    # orderitems = OrderItem.objects.all()
    orderitems = OrderItem.objects.filter(
        product__user=request.user).order_by('-date_orderd')
    address = ShippingAddress.objects.filter(
        order__in=Subquery(orderitems.values('order'))).order_by('-date_orderd')
    detail = zip(order, orderitems, address)
    return render(request, "sellerprofile/selling.html", {'detail': detail, 'uid': uid})


def adminhome(request):
    order = Order.objects.filter(user=request.user).select_related(
        'user')
    address = ShippingAddress.objects.select_related('order')
    uid = request.user.id
    # orderitems = OrderItem.objects.filter(product.user == request.user.id)
    orderitems = OrderItem.objects.select_related('product', 'order')
    detail = zip(order, orderitems, address)
    total_product = Product.objects.filter(user=request.user).count()
    # order_count = OrderItem.objects.filter().select_related('product')
    total_orders = OrderItem.objects.filter(
        product__user=request.user).count()
    return render(request, "sellerprofile/home.html", {'total_product': total_product, 'detail': detail, 'uid': uid, 'total_orders': total_orders})
