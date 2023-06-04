import calendar
from django.urls import reverse_lazy

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.http.response import HttpResponseRedirect
from .models import Banner, Category, Brand, Product, ProductAttribute, CartOrder, CartOrderItems, ProductReview, \
    Wishlist, UserAddressBook
from django.db.models import Max, Min, Count, Avg
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string

from .forms import UserPasswordChangeForm, UserLoginForm
from .forms import SignupForm, ReviewAdd, AddressBookForm, ProfileForm

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LoginView, LogoutView


# Home Page
def home(request):
    banners = Banner.objects.all().order_by('-id')
    data = Product.objects.filter(is_featured=True).order_by('-id')
    return render(request, 'index.html', {'data': data, 'banners': banners})


# Category
def category_list(request):
    data = Category.objects.all().order_by('-id')
    return render(request, 'category_list.html', {'data': data})


# Brand
def brand_list(request):
    data = Brand.objects.all().order_by('-id')
    return render(request, 'brand_list.html', {'data': data})


# Product List
def product_list(request):
    total_data = Product.objects.count()
    data = Product.objects.all().order_by('-id')
    min_price = Product.objects.aggregate(Min('price'))
    max_price = Product.objects.aggregate(Max('price'))
    return render(request, 'product_list.html',
                  {
                      'data': data,
                      'total_data': total_data,
                      'min_price': min_price,
                      'max_price': max_price,
                  }
                  )


# Product List According to Category
def category_product_list(request, cat_id):
    category = Category.objects.get(id=cat_id)
    data = Product.objects.filter(category=category).order_by('-id')
    return render(request, 'category_product_list.html', {
        'data': data,
    })


# Product List According to Brand
def brand_product_list(request, brand_id):
    brand = Brand.objects.get(id=brand_id)
    data = Product.objects.filter(brand=brand).order_by('-id')
    return render(request, 'category_product_list.html', {
        'data': data,
    })


# Product Detail
def product_detail(request, slug, id):
    product = Product.objects.get(id=id)

    colors = ProductAttribute.objects.filter(product=product).values('color__id', 'color__title',
                                                                     'color__color_code').distinct()

    sizes = ProductAttribute.objects.filter(product=product).values('size__id', 'size__title', 'color__id').distinct()
    reviewForm = ReviewAdd()

    # Check
    canAdd = True

    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
        if reviewCheck > 0:
            canAdd = False
    # End

    # Fetch reviews
    reviews = ProductReview.objects.filter(product=product)
    # End

    # Fetch avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    # End

    return render(request, 'product_detail.html',
                  {'data': product, 'colors': colors, 'sizes': sizes,
                   'reviewForm': reviewForm, 'canAdd': canAdd, 'reviews': reviews, 'avg_reviews': avg_reviews})


# Search
def search(request):
    q = request.GET['q']
    data = Product.objects.filter(title__icontains=q).order_by('-id')
    return render(request, 'search.html', {'data': data})


# Filter Data
def filter_data(request):
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    minPrice = request.GET['minPrice']
    maxPrice = request.GET['maxPrice']
    allProducts = Product.objects.all().order_by('-id').distinct()
    allProducts = allProducts.filter(productattribute__price__gte=minPrice)
    allProducts = allProducts.filter(productattribute__price__lte=maxPrice)
    if len(colors) > 0:
        allProducts = allProducts.filter(productattribute__color__id__in=colors).distinct()
    if len(categories) > 0:
        allProducts = allProducts.filter(category__id__in=categories).distinct()
    if len(brands) > 0:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()
    if len(sizes) > 0:
        allProducts = allProducts.filter(productattribute__size__id__in=sizes).distinct()
    t = render_to_string('ajax/product-list.html', {'data': allProducts})
    return JsonResponse({'data': t})


# Add to cart
def add_to_cart(request):
    cart_p = {}
    cart_p[str(request.GET['id'])] = {
        'image': request.GET['image'],
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
    }
    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_p[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cartdata'] = cart_data
        else:
            cart_data = request.session['cartdata']
            cart_data.update(cart_p)
            request.session['cartdata'] = cart_data
    else:
        request.session['cartdata'] = cart_p
    return JsonResponse({'data': request.session['cartdata'], 'totalitems': len(request.session['cartdata'])})


# Cart List Page
def cart_list(request):
    total_amt = 0
    if 'cartdata' in request.session:
        for p_id, item in request.session['cartdata'].items():
            total_amt += int(item['qty']) * float(item['price'])
        return render(request, 'cart.html',
                      {'cart_data': request.session['cartdata'], 'totalitems': len(request.session['cartdata']),
                       'total_amt': total_amt})
    else:
        return render(request, 'cart.html', {'cart_data': '', 'totalitems': 0, 'total_amt': total_amt})


# Delete Cart Item
def delete_cart_item(request):
    p_id = str(request.GET['id'])
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            del request.session['cartdata'][p_id]
            request.session['cartdata'] = cart_data
    total_amt = 0
    for p_id, item in request.session['cartdata'].items():
        total_amt += int(item['qty']) * float(item['price'])

    t = render_to_string('ajax/cart-list.html',
                         {'cart_data': request.session['cartdata'], 'totalitems': len(request.session['cartdata']),
                          'total_amt': total_amt})

    return JsonResponse({'data': t, 'totalitems': len(request.session['cartdata'])})


def update_cart_item(request):
    p_id = str(request.GET['id'])
    p_qty = request.GET['qty']
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = p_qty
            request.session['cartdata'] = cart_data
    total_amt = 0
    for p_id, item in request.session['cartdata'].items():
        total_amt += int(item['qty']) * float(item['price'])
    t = render_to_string('ajax/cart-list.html',
                         {'cart_data': request.session['cartdata'], 'totalitems': len(request.session['cartdata']),
                          'total_amt': total_amt})
    return JsonResponse({'data': t, 'totalitems': len(request.session['cartdata'])})


# Signup Form
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=pwd)
            login(request, user)
            return redirect('home')
    form = SignupForm
    return render(request, 'registration/signup.html', {'form': form})


# Checkout
@login_required
def checkout(request):
    # total_amt = 0
    totalAmt = 0

    if 'cartdata' in request.session:
        for p_id, item in request.session['cartdata'].items():
            totalAmt += int(item['qty']) * float(item['price'])

        request.session['totalAmt'] = totalAmt
        address = UserAddressBook.objects.filter(user=request.user, status=True).first()

        return render(request, 'checkout.html',
                      {'cart_data': request.session['cartdata'],
                       'totalitems': len(request.session['cartdata']), 'total_amt': totalAmt,
                       'address': address})

# Checkout
@login_required
def create_order(request):
    # Order
    order = CartOrder.objects.create(
        user=request.user,
        total_amt=request.session.get('totalAmt'),
        order_status='process'
    )
    # End

    total_amt = 0

    for p_id, item in request.session['cartdata'].items():
        total_amt += int(item['qty']) * float(item['price'])
        # OrderItems
        items = CartOrderItems.objects.create(
            order=order,
            invoice_no='INV-' + str(order.id),
            item=item['title'],
            image=item['image'],
            qty=item['qty'],
            price=item['price'],
            total=float(item['qty']) * float(item['price'])
        )

    del request.session['cartdata']
    return HttpResponseRedirect(reverse_lazy('my_dashboard'))


# Save Review
def save_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user
    review = ProductReview.objects.create(
        user=user,
        product=product,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating'],
    )
    data = {
        'user': user.username,
        'review_text': request.POST['review_text'],
        'review_rating': request.POST['review_rating']
    }

    # Fetch avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    # End

    return JsonResponse({'bool': True, 'data': data, 'avg_reviews': avg_reviews})


# User Dashboard


def my_dashboard(request):
    orders = CartOrder.objects.annotate(month=ExtractMonth('order_dt')).values('month').annotate(
        count=Count('id')).values('month', 'count').filter(user=request.user).order_by('-id')

    monthNumber = {}
    totalOrders = []

    for d in orders:
        if calendar.month_name[d['month']] in monthNumber.keys():
            monthNumber[calendar.month_name[d['month']]] += d['count']
        else:
            monthNumber[calendar.month_name[d['month']]] = d['count']

    print(list(monthNumber.keys()))
    print(list(monthNumber.values()))

    return render(request, 'user/dashboard.html', {'monthNumber': list(monthNumber.keys()),
                                                   'totalOrders': list(monthNumber.values())})


# My Orders
def my_orders(request):
    orders = CartOrder.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user/orders.html', {'orders': orders})


# Order Detail
def my_order_items(request, id):
    order = CartOrder.objects.get(pk=id)
    orderitems = CartOrderItems.objects.filter(order=order).order_by('-id')
    return render(request, 'user/order-items.html', {'orderitems': orderitems})


# My Reviews
def my_reviews(request):
    reviews = ProductReview.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user/reviews.html', {'reviews': reviews})


# My AddressBook
def my_addressbook(request):
    addbook = UserAddressBook.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user/addressbook.html', {'addbook': addbook})


# Save addressbook
def save_address(request):
    msg = None
    if request.method == 'POST':
        form = AddressBookForm(request.POST)
        if form.is_valid():
            saveForm = form.save(commit=False)
            saveForm.user = request.user
            if 'status' in request.POST:
                UserAddressBook.objects.update(status=False)
            saveForm.save()
            msg = 'Data has been saved'
    form = AddressBookForm
    return render(request, 'user/add-address.html', {'form': form, 'msg': msg})


# Activate address
def activate_address(request):
    a_id = str(request.GET['id'])
    UserAddressBook.objects.update(status=False)
    UserAddressBook.objects.filter(id=a_id).update(status=True)
    return JsonResponse({'bool': True})


# Edit Profile
def edit_profile(request):
    msg = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            msg = 'Data has been saved'
    form = ProfileForm(instance=request.user)
    return render(request, 'user/edit-profile.html', {'form': form, 'msg': msg})


# Update addressbook
def update_address(request, id):
    address = UserAddressBook.objects.get(pk=id)
    msg = None
    if request.method == 'POST':
        form = AddressBookForm(request.POST, instance=address)
        if form.is_valid():
            saveForm = form.save(commit=False)
            saveForm.user = request.user
            if 'status' in request.POST:
                UserAddressBook.objects.update(status=False)
            saveForm.save()
            msg = 'Data has been saved'
    form = AddressBookForm(instance=address)
    return render(request, 'user/update-address.html', {'form': form, 'msg': msg})


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'registration/login.html'
    next_page = 'home'
    success_message = 'Добро пожаловать на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'home'


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'user/user_password_change.html'
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля на сайте'
        return context

    def get_success_url(self):
        return reverse_lazy('my_dashboard')
