from django.urls import path
from . import views
from .views import (blogsView, AddCategoryView, EditProductView, DeleteProductView, EditCartItemView,
                    AddProductView, EditPaymentView, DeletePaymentView, OrderSummaryView, DeleteCartItemView,
                   
                    )

from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    # path('', views.home, name='home'),
    path("", blogsView.as_view(), name="blogsView"),

    #checkout session
    path('create/', views.payment_init, name='create'),
    path('process/', views.payment_process, name='process'),
    path('success/', views.payment_success, name='success'), 
    path('canceled/', views.payment_canceled, name='canceled'),
    path('webhook/', views.stack_webhook, name='stack-webhook'),

    #category
    path("category/<str:cats>/", views.CategoryView, name="category"),
    path("category-list/", views.CategoryListView, name="category-list"),
    path("add_category/", AddCategoryView.as_view(), name="add_category"),

    #inventory
    path('inventory/', views.inventory, name='inventory'),
    path('payment_detail/<str:pk>/', views.payment, name='payment_detail'),
    path("edit_payment/<str:pk>/", EditPaymentView.as_view(), name="edit_payment"),
    path("delete_payment/<str:pk>/", DeletePaymentView.as_view(), name="delete_payment"),

    #search
    path('search/', views.search, name='search'),

    #product
    path('product_detail/<str:pk>/', views.product, name='product_detail'),
    path("add_product/", AddProductView.as_view(), name="add_product"),
    path("edit_product/<str:pk>/", EditProductView.as_view(), name="edit_product"),
    path("delete_product/<str:pk>/", DeleteProductView.as_view(), name="delete_product"),

    #cart
    path('add-to-cart/<str:pk>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<str:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path("order-summary/", OrderSummaryView.as_view(), name="order-summary"),
    path("edit-cart-item/<str:pk>/", EditCartItemView.as_view(), name="edit-cart-item"),
    path("delete-cart-item/<str:pk>/", DeleteCartItemView.as_view(), name="delete-cart-item"),
    path('remove-single-item-from-cart/<str:pk>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    
    #authentication
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    # path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
