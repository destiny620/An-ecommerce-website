from django.contrib import admin
from .models import Product, Category, Payment, CartItem, Profile



# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'phone_no', 'email', 'city', 'paid', 'updated' 
    ]

    list_filter = ['paid', 'created', 'updated']

admin.site.register(Product),
admin.site.register(Category),
admin.site.register(CartItem),
admin.site.register(Profile),




