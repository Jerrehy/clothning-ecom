from django.urls import path
from . import views
from .views import UserPasswordChangeView, UserLoginView, UserLogoutView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('search', views.search, name='search'),
    path('category-list', views.category_list, name='category-list'),
    path('brand-list', views.brand_list, name='brand-list'),
    path('product-list', views.product_list, name='product-list'),
    path('category-product-list/<int:cat_id>', views.category_product_list, name='category-product-list'),
    path('brand-product-list/<int:brand_id>', views.brand_product_list, name='brand-product-list'),
    path('product/<str:slug>/<int:id>', views.product_detail, name='product_detail'),
    path('filter-data', views.filter_data, name='filter_data'),
    path('add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('cart', views.cart_list, name='cart'),
    path('delete-from-cart', views.delete_cart_item, name='delete-from-cart'),
    path('update-cart', views.update_cart_item, name='update-cart'),

    path('accounts/signup', views.signup, name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-change', UserPasswordChangeView.as_view(), name='password-change'),


    path('checkout', views.checkout, name='checkout'),
    path('create-order', views.create_order, name='create-order'),

    path('save-review/<int:pid>', views.save_review, name='save-review'),

    # User Section Start
    path('my-dashboard', views.my_dashboard, name='my_dashboard'),
    path('my-orders', views.my_orders, name='my_orders'),
    path('my-orders-items/<int:id>', views.my_order_items, name='my_order_items'),
    # End

    # My Reviews
    path('my-reviews', views.my_reviews, name='my-reviews'),

    # My AddressBook
    path('my-addressbook', views.my_addressbook, name='my-addressbook'),
    path('add-address', views.save_address, name='add-address'),
    path('activate-address', views.activate_address, name='activate-address'),
    path('update-address/<int:id>', views.update_address, name='update-address'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
