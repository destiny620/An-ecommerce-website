from django.shortcuts import render, redirect,  get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import AuthenticationForm
from django.http.response import HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.core.mail import send_mail
from django.conf import settings
from django.views import View
from django.http import HttpResponse
# from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, View, TemplateView
# from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import *
from .forms import *
from django.urls import reverse_lazy
# from cart.cart import Cart
import json
import requests
import hmac
import hashlib
# import xlsxwriter


api_key = settings.PAYSTACK_TEST_SECRET_KEY
url = settings.PAYSTACK_INITIALIZE_PAYMENT_URL

# Create your views here.


def register(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			messages.success(request, "Registration successful." )
			return redirect("/")
     
	messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request, "register.html", {"form":form})


def login(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				auth.login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("/")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "login.html", {"form":form})


def logout(request):
	auth.logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/")

def profile(request):
    #  profile = Profile.objects.all()
     return render(request, 'profile.html')

def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method=="POST":
        form = ProfileForm(data=request.POST, files=request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            alert = True
            return render(request, "edit_profile.html", {'alert':alert})
    else:
        form=ProfileForm(instance=profile)
    return render(request, "edit_profile.html", {'form':form})

# class EditProfileView(UpdateView):
#     model = Profile
#     form_class = Editprofileform
#     template_name = 'edit_profile.html'
#     success_url = reverse_lazy('profile')


class blogsView(LoginRequiredMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'home'
    model = Product 
    template_name = 'home.html'
    # ordering = ['-created_at']
    paginate_by = 6
    cats = Category.objects.all()
  
  
    
    
    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(blogsView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
       
        return context
    
   
    

def CategoryView(request, cats):
    categorys = Product.objects.filter(category=cats)
    return render(request, 'category.html', {'cats': cats, 'categorys': categorys})


def CategoryListView(request):
    cat_menu_list = Product.objects.all()
    return render(request, 'category_list.html', {'cat_menu_list': cat_menu_list})


# def CategoryListView(request):
#     cat_menu_list = Category.objects.all()
#     return render(request, 'category_list.html', {'cat_menu_list': cat_menu_list})


class AddCategoryView(CreateView):
    model = Category
    template_name = 'add_category.html'
    fields = ['name']
    success_url = reverse_lazy('blogsView')


def product(request, pk):
    products = Product.objects.get(id=pk)
    # product = Product.objects.filter(category=products.category).exclude(id=pk)[:4] #related product not more than 4
    product = Product.objects.filter(category=products.category).exclude(id=pk)
    stock = Product.objects.filter(manufacturer=products.manufacturer)
    sold_out = stock.count()
    
    if sold_out <= 1:
       print('sold out')
       messages.info(request, 'one product remaining, almost sold out')
    else:
         print('in stock')
         messages.info(request, 'in stock')

    context = {
         'products':products,
         'product':product,
         'sold_out':sold_out
    }

    return render(request, 'product_detail.html', context)

class AddProductView(CreateView):
    model = Product
    form_class = createproductform
    template_name = 'add_product.html'
    success_url = reverse_lazy('blogsView')

class EditProductView(UpdateView):
    model = Product
    form_class = Editproductform
    template_name = 'edit_product.html'
    success_url = reverse_lazy('blogsView')


class DeleteProductView(DeleteView):
    model = Product
    template_name = 'delete_product.html'
    success_url = reverse_lazy('blogsView')


def inventory(request):
    payments = Payment.objects.all()
    products = Product.objects.all()

    # total_orders = orders.count()
    total_orders = payments.count()
    total_products = products.count()
    # paid = payments.filter().count()
    # pending = payments.filter(status='pending').count()

    context = {
        'payments':payments,
        'products':products,
        'total_orders':total_orders,
        # 'total_customers':total_customers,
        'total_products':total_products,
        # 'paid':paid,
        # 'pending':pending,
    }
    
    return render(request, 'inventory.html', context)


def payment(request, pk):
    payments = Payment.objects.get(id=pk)
    return render(request, 'payment_detail.html', {'payments': payments})


class EditPaymentView(UpdateView):
    model = Payment
    form_class = EditOrderform
    template_name = 'edit_payment.html'
    success_url = reverse_lazy('blogsView')


class DeletePaymentView(DeleteView):
    model = Payment
    template_name = 'delete_payment.html'
    success_url = reverse_lazy('blogsView')

def add_to_cart(request, pk):
     product = get_object_or_404(Product, id=pk)
     cart_item, created = CartItem.objects.get_or_create(
          product=product,
          user=request.user,
          ordered=False, 
     )

     order_qs = Payment.objects.filter(user=request.user)
     if order_qs.exists():
          order = order_qs[0]
          #check if the order item is in the order
          if order.cartItem.filter(id=product.pk).exists():
               cart_item.quantity += 1
               cart_item.save()

          else:
               order.cartItem.add(cart_item)
     else:
          created = datetime.today()
          order = Payment.objects.create(
               user=request.user, created=created, amount=product.price
          )
          order.cartItem.add(cart_item)
     return redirect('order-summary')


def remove_from_cart(request, pk):
     product = get_object_or_404(Product, id=pk)
     order_qs = Payment.objects.filter(
          user=request.user,
      
           
     )
     if order_qs.exists():
          order = order_qs[0]
          #check if the order item is in the order
          if order.cartItem.filter(id=product.pk).exists():
               cart_item = CartItem.objects.filter(
                    product=product,
                    user=request.user,
                    odered=False
                   
               )[0]
               order.cartItem.remove(cart_item)
               messages.info(request, 'This item was remove from your cart')
               return redirect('order-summary')
          else:
               messages.info(request, 'This item was not in your cart')
               return redirect('order-summary')
     else:
          messages.info(request, 'You do not have an active order')
          return redirect('order-summary')
     

def remove_single_item_from_cart(request, pk):
     product = get_object_or_404(Product, id=pk)
     order_qs = Payment.objects.filter(
          user=request.user,
           
     )
     if order_qs.exists():
          order = order_qs[0]
          #check if the order item is in the order
          if order.cartItem.filter(id=product.pk).exists():
               cart_item = CartItem.objects.filter(
                    product=product,
                    user=request.user,
                    ordered=False
                   
               )[0]
               cart_item.quantity -= 1
               cart_item.save()
              
               messages.info(request, 'This item quantity was updated')
               return redirect('order-summary')
          else:
               messages.info(request, 'This item was not in your cart')
               return redirect('order-summary')
     else:
          messages.info(request, 'You do not have an active order')
          return redirect('order-summary')
     

class EditCartItemView(UpdateView):
    model = CartItem
    form_class = EditCartItemform
    template_name = 'edit_cart_item.html'
    success_url = reverse_lazy('order-summary')


class DeleteCartItemView(DeleteView):
    model = CartItem
    template_name = 'delete_cart_item.html'
    success_url = reverse_lazy('order-summary')


        

class OrderSummaryView(View):
     def get(self, *args, **kwargs):
          
          try:
               order = Payment.objects.get(user=self.request.user)
               context = {
                    'object': order
               }
               return render(self.request, 'add_cart.html', context)
          except ObjectDoesNotExist:
               messages.error(self.request, 'You donot have an active order')
               return redirect('/')


# def cart_detail(request):
#      return render(request, 'add_cart.html')


def search(request):
    if request.method == 'GET':
        query= request.GET.get('q')

        submitbutton= request.GET.get('submit')

        if query is not None:

            lookups= Q(manufacturer__icontains=query) | Q(category__icontains=query)

            results= Product.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton}

            return render(request, 'search.html', context)

        else:
            return render(request, 'search.html')

    else:
        return render(request, 'search.html')



def payment_init(request):
    if request.method == 'POST':
        # get form data if POST request
        form = PaymentInitForm(request.POST)

        # validate form before saving
        if form.is_valid():
            payment = form.save(commit=False)
            payment.save()
            # set the payment in the current session
            request.session['payment_id'] = payment.id
            # message alert to confirm payment intializaton
            messages.success(request, "Payment Initialized Successfully." )
            # redirect user for payment completion
            return redirect(reverse('process'))
    else:
    # render form if GET request
        form = PaymentInitForm()
    return render(request, 'create.html', {'form': form})


def payment_process(request):
    # retrive the payment_id we'd set in the djago session ealier
   
    payment_id = request.session.get('payment_id', None)
    # using the payment_id, get the database object
    payment = get_object_or_404(Payment, id=payment_id)
    
    # retrive payment amount 
    amount = payment.get_amount()
    # amount = payment.get_total()
    # cart = payment.cartItem

    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('success'))
        cancel_url = request.build_absolute_uri(
            reverse('canceled'))

        # metadata to pass additional data that 
        # the endpoint doesn't accept naturally.
        metadata= json.dumps({"payment_id":payment_id,  
                              "cancel_action":cancel_url, 
                              
                            })

        # Paystack checkout session data
        session_data = {
            'email': payment.email,
            'amount': int(amount),
            # 'cart' : cart,
            # 'product':payment.product,
            'callback_url': success_url,
            'metadata': metadata
            }

        headers = {"authorization": f"Bearer {api_key}"}
        # API request to paystack server
        r = requests.post(url, headers=headers, data=session_data)
        response = r.json()
        if response["status"] == True :
            # redirect to Paystack payment form
            try:
                redirect_url = response["data"]["authorization_url"]
                return redirect(redirect_url, code=303)
            except:
                pass
        else:
            return render(request, 'process.html', locals())
    else:
        return render(request, 'process.html', locals())
    
#  C:\Users\USER\AppData\Local/ngrok/ngrok.yml
def payment_success(request):
     # retrive the payment_id we'd set in the django session ealier
    payment_id = request.session.get('payment_id', None)#new
    # using the payment_id, get the database object
    payment = get_object_or_404(Payment, id=payment_id)#new

    # retrive the query parameter from the request object
    ref = request.GET.get('reference', '')#new
    # verify transaction endpoint
    url = 'https://api.paystack.co/transaction/verify/{}'.format(ref)#new

    # set auth headers
    headers = {"authorization": f"Bearer {api_key}"}#new
    r = requests.get(url, headers=headers)#new
    res = r.json()#new
    res = res["data"]

    # verify status before setting payment_ref
    if res['status'] == "success":  # new
        # update payment payment reference
        payment.paystack_ref = ref #new
        payment.save()#new
    return render(request, 'success.html')


def payment_canceled(request):
    return render(request, 'canceled.html')



@csrf_exempt
def stack_webhook(request):
    # retrive the payload from the request body
    payload = request.body
    # signature header to to verify the request is from paystack
    sig_header = request.headers['x-paystack-signature']
    body = None
    event = None

    try:
        # sign the payload with `HMAC SHA512`
        hash = hmac.new(api_key.encode('utf-8'), payload, digestmod=hashlib.sha512).hexdigest()
        # compare our signature with paystacks signature
        if hash == sig_header:
            # if signature matches, 
            # proceed to retrive event status from payload
            body_unicode = payload.decode('utf-8')
            body = json.loads(body_unicode)
            # event status
            event = body['event']
        else:
            raise Exception
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except KeyError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except:
        # Invalid signature
        return HttpResponse(status=400)

    if event == 'charge.success':
        # if event status equals 'charge.success'
        # get the data and the `payment_id` 
        # we'd set in the metadata ealier
        data, payment_id = body["data"], body['data']['metadata']['payment_id']

        # validate status and gateway_response
        if (data["status"] == 'success') and (data["gateway_response"] == "Successful"):
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                return HttpResponse(status=404)
            # mark payment as paid
            payment.paid = True
            payment.save(force_update=True)

            print("PAID")

    return HttpResponse(status=200)

# def excelApi(request):
#     wb = Workbook(FileFormatType.XLSX)
# # insert value in the cells
#     wb.getWorksheets().get(0).getCells().get("A1").putValue("Hello World!")
# # save workbook as .xlsx file
#     wb.save("workbook.xlsx")

#     return redirect('/')


# # Workbook() takes one, non-optional, argument
# # which is the filename that we want to create.
# workbook = xlsxwriter.Workbook('hello.xlsx')
 
# # The workbook object is then used to add new
# # worksheet via the add_worksheet() method.
# worksheet = workbook.add_worksheet()
 
# # Use the worksheet object to write
# # data via the write() method.
# worksheet.write('A1', 'Hello..')
# worksheet.write('B1', 'Geeks')
# worksheet.write('C1', 'For')
# worksheet.write('D1', 'Geeks')
 
# # Finally, close the Excel file
# # via the close() method.
# workbook.close()