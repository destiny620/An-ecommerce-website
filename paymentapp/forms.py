from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User



choices = Category.objects.all().values_list('name','name')

choice_list = []
for item in choices:
    choice_list.append(item)

class PaymentInitForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['first_name', 'last_name', 'email', 'amount', 'city', 'phone_no',]
       


class createproductform(forms.ModelForm):
    class Meta:
        model=Product
        fields= ('manufacturer', 'price', 'discount_price', 'description', 'category', 'image', 'created_at')
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class':'form-control'}),
            'price': forms.NumberInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'category': forms.Select(choices=choice_list, attrs={'class':'form-control'}),
        }

class Editproductform(forms.ModelForm):
    class Meta:
        model=Product
        fields= ('manufacturer', 'price', 'discount_price', 'description', 'category', 'image', 'created_at')


class EditOrderform(forms.ModelForm):
    class Meta:
        model=Payment
        fields= "__all__"
 
class EditCartItemform(forms.ModelForm):
    class Meta:
        model=CartItem
        fields= ('quantity',)

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields= "__all__"


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


        