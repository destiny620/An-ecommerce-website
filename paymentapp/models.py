from datetime import timezone
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User, auth
from django.conf import settings
from django.urls import reverse
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_no = models.IntegerField(blank=True, null=True)
    facebook = models.CharField(max_length=300, blank=True, null=True)
    twitter = models.CharField(max_length=300, blank=True, null=True)
    instagram = models.CharField(max_length=300, blank=True, null=True)
    linkedin = models.CharField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        return str(self.user)


class Category(models.Model):
    name = models.CharField(max_length=30, null=True)
   

    def __str__(self):
        return self.name
    

class Product(models.Model):
    manufacturer = models.CharField(max_length=200, null=True, default=now)
    price = models.IntegerField(default=1)
    discount_price = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    category = models.CharField(max_length=30, default='categorised')
    image = models.ImageField(upload_to="profile_pics",null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return self.manufacturer
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={
            'id': self.pk
        })
    
    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'id': self.pk
        })
    
    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            'id': self.pk
        })
    
   
    

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.product.manufacturer}"
     
    def get_total_item_price(self):
        return self.quantity * self.product.price
    
    def get_total_discount_price(self):
        return self.quantity * self.product.discount_price
    
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_price()
    
    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()
    
    # def __str__(self):
    #     return self.user.username
    



class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_no = models.IntegerField(null=True)
    email = models.EmailField()
    cartItem = models.ManyToManyField(CartItem)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)
    paystack_ref = models.CharField(max_length=15, blank=True)
    paid = models.BooleanField(default=False)
  


    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Payment {self.id}'
    

    def get_amount(self):
        return self.amount  * 100
    
    def get_total(self):
        total=0
        for cart_item in self.cartItem.all():
            total += cart_item.get_final_price()
        return total
    
   
    
   
    

# class Cart(models.Model):
#     cart_id = models.CharField(max_length=250, blank=True)
#     date_added = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.card_id


# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=1)
#     is_active = models.BooleanField(blank=True)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

#     def sub_total(self):
#         return self.product.price * self.quantity
    
#     def __str__(self):
#         return self.product