from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone 
from .forms import *
from decimal import Decimal
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from accounts.models import *
from allauth.socialaccount.models import SocialAccount, SocialToken
import requests, json
from django.db.models.functions import Replace
from django.db.models import Value
# Create your views here.

def person(request):
    profile = Profile.objects.get_username()
    users = User.objects.get(user=request.user)
    return render(request, 'base.html', {'profile':profile, 'users':users})

def home(request):
    foods = Food.objects
    food_list = Food.objects.all()
    paginator = Paginator(food_list,4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'home.html', {'foods':foods, 'posts':posts})

# 고객이 보는 나의 요청내역
def myCart(request):
    request_list = Cart.objects.all().filter(sender=request.user)
    # print(type(request_list))
    return render(request, 'myCart.html', {'request_list':request_list})

# 매장이 보는 나의 요청온내역 
def requested_cart(request):
    the_receiver = Profile.objects.get(user=request.user)
    requested_list = Cart2.objects.all().filter(receiver=the_receiver)
    return render(request, 'requested_cart.html', {'request_list':requested_list})

# 매장이 보는 지난 요청 내역
# def past(request):
#     me = Profile.objects.get(user=request.user)
#     past = Cart3.objects.all().filter(receiver=me)
#     past = past.order_by('-date')
#     if request.method == 'POST':
#         customer = User.objects.get(username=request.POST['sender'])
#         whose = me
#         reason = 'accept'
#         other = ''
#         how_many = 1
#         custom = Customer(customer=customer, whose=whose, reason=reason, others=other, how_many=how_many)
#         custom.save()
#         return redirect('myCustomer')
#     return render(request, 'past.html', {'past':past})

# # 매장이 보는 나한테 요청한 고객
# def myCustomers(request):
#     me = Profile.objects.get(user=request.user)
#     myCus = Customer.objects.all().filter(whose=me)
#     return render(request, 'myCustomers.html', {'customers':myCus})
    
# 매장이 보는 게시글관리 
def post_retrieve(request):
    the_author = Profile.objects.get(user=request.user)
    post_list = Food.objects.all().filter(author=the_author)
    return render(request, 'myPostList.html', {'post_list':post_list})

def detail(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    return render(request, 'detail.html', {'food':food_detail})

@login_required
def add_comment_to_food(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = food_detail
            comment.save()
            return redirect('detail', food_id=food_id)
        else:
            form = CommentForm()
        return render(request, 'comment.html', {'form':form})

# 결제 전 고객이 자신의 요청 내역을 보는 카트를 저장
@login_required
def cart(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        people = request.POST['people']
        total_price = request.POST['total_price']
        sender = request.user
        receiver = food_detail.author
        the_title = Food.objects.get(title=food_detail.title)
        # request_date = timezone.now()
        cart = Cart(sender=request.user, people=people, total_price=total_price, receiver=receiver, title=the_title)
        cart.save()
        return redirect('myCart')
        # my내역에서 확인할 수 있도록 페이지 만들고 바꾸기
    return render(request, 'detail.html', {'error':'요청실패', 'food':food_detail})


# 결제준비를 마친 고객이 결제 완료되었다는 문구를 보는 페이지 
def successPage(request):
    access_token = SocialToken.objects.get(account__user=request.user, account__provider="kakao").token
    pg_token = request.GET['pg_token']
    print("@@@@@@@@@@@@@@@@@@@@@@@@ pg_token : {} , ".format(pg_token))
    cart2 = Cart2.objects.get(sender=request.user)
    if request.method == 'POST':
        return render(request, 'ordering.html')
    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'Content-Type':'application/x-www-form-urlencoded;charset=utf-8'
    }
    data = {
        "cid": "TC0ONETIME",
        "partner_order_id": cart2.order_id,
        "partner_user_id": cart2.receiver,
        "pg_token": pg_token,
        "tid": cart2.tid
    }
    res = requests.post(URL,headers=headers,data=data)
    print("@@@@@@ {} @@@@@@@@@@@ {}".format(res.status_code, cart2.status))
    if res.status_code == 200:
        cart2 = Cart2.objects.get(sender=request.user)
        cart2.status = "1"
        cart2.save()
        return render(request, 'check_success.html')
    else:
        cart2 = Cart2.objects.get(sender=request.user)
        cart2.status = "-1"
        cart2.save()
        return redirect('fail')

# 결제준비가 된 고객의 주문을 매장이 볼 수 있도록 cart2모델에 저장하기 
def successCart(request, cart_id):
    cart_detail = get_object_or_404(Cart, pk=cart_id)
    if request.method == 'POST':
        sender = cart_detail.sender
        receiver = cart_detail.receiver
        people = cart_detail.people
        total_price = cart_detail.total_price
        request_date = timezone.now()
        title = cart_detail.title
        cart2 = Cart2(sender=sender, receiver=receiver, people=people, total_price=total_price, request_date=request_date, title=title)
        cart2.save()
        return redirect('home')
    else:
        return render(request, 'ordering.html', {'cart':cart_detail})

def foodpost(request):
    if request.method == 'POST':
        form = FoodPost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            the_author = Profile.objects.get(user=request.user)
            post.author = the_author
            post.pub_date=timezone.now()
            post.save()
            return redirect('home')
    else:
        form = FoodPost()
    return render(request,'new.html', {'form':form})

def edit(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        form = FoodPost(request.POST, request.FILES, instance=food_detail)
        if form.is_valid():
            post = form.save(commit=False)
            the_author = Profile.objects.get(user=request.user)
            post.author = the_author
            post.pub_date=timezone.now()
            post.save()
            return redirect('detail', food_id=food_id)
            # 게시글 관리에서 수정할 수 있게 옮기자(게시글 관리 페이지 만들면)
    else:
        form = FoodPost(instance=food_detail)
    return render(request, 'edit.html', {'form':form})        

            
def search(request):
    search = request.GET['searchkeyword']
    posts = Food.objects.filter(title__icontains=search) | Food.objects.filter(category__icontains=search) | Food.objects.filter(category2__icontains=search) 
    return render(request,'search.html',{'posts':posts})

def delete(request, food_id):
    deleted_food = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        deleted_food.delete()
        return redirect('myposts')

# 결제 준비 
@login_required
def checkplz(request):
    access_token = SocialToken.objects.get(account__user=request.user, account__provider="kakao").token
    print(access_token)
    partner_user_id = Profile.objects.get(nickname=request.POST['receiver'])
    quantity = request.POST['people']
    total_amount = request.POST['total_price']
    item_name = Food.objects.get(title=request.POST['title'])
    partner_order_id = Cart.objects.get(id=request.POST['cart_id']).id
    data = {
        "cid": "TC0ONETIME",
        "partner_order_id": partner_order_id,
        "partner_user_id": partner_user_id,
        "item_name": item_name,
        "quantity": quantity,
        "total_amount": total_amount,
        "vat_amount": 0,
        "tax_free_amount": 0,
        "approval_url": "http://localhost:8000/success/",
        "fail_url": "http://localhost:8000/fail",
        "cancel_url": "http://localhost:8000/fail"   
    }
    URL = 'https://kapi.kakao.com/v1/payment/ready'
    ## http header를 보내는데, 여기에 Content-Type이나 권한인증을 위한 Token
    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'Content-Type':'application/x-www-form-urlencoded;charset=utf-8'
    }
    res = requests.post(URL,headers=headers,data=data)
    ## 받아온 데이터를 Json => Dict으로 바꿈.(파이썬에서 사용 가능하게)
    if res.status_code == 200:
        resp = json.loads(res.text)
        cart2 = Cart2(
            tid=resp['tid'],order_id=partner_order_id,
            sender=request.user, receiver=partner_user_id, people=quantity, 
            total_price=total_amount, request_date=timezone.now(), title=item_name,status="0")
        cart2.save()
        print("@@@@@@@@@@@ order id = {} , tid = {}".format(partner_order_id , resp['tid']))
        return redirect(resp['next_redirect_pc_url'])
    else:
        return redirect('fail')
    

def checkCanceled(request, cart2_id):
    cart2 = get_object_or_404(Cart2, order_id=cart2_id)
    access_token = SocialToken.objects.get(account__user=cart2.sender, account__provider="kakao").token
    if request.method == 'POST':
        # 거절을 누른 경우
        if request.POST['deny']:
            cart2.status == "-1"
            headers = {
                    'Authorization': 'Bearer ' + str(access_token),
                    'Content-Type':'application/x-www-form-urlencoded;charset=utf-8'
                }
            data = {
                    "cid": "TC0ONETIME",
                    "partner_order_id": cart2.order_id,
                    "cancel_amount": cart2.total_price,
                    "cancel_vat_amount": 0,
                    "cancel_tax_free_amount": 0,
                    "tid": cart2.tid
                }
            URL = 'https://kapi.kakao.com/v1/payment/cancel'
            res = requests.post(URL,headers=headers,data=data)
            cart2.save()
            sender = cart2.sender
            receiver = cart2.receiver
            order_id = cart2.order_id
            people = cart2.people
            total_price = cart2.total_price
            date = timezone.now()
            title = cart2.title
            status = '-1'
            cart3 = Cart3(sender=sender, receiver=receiver, order_id=order_id, people=people, total_price=total_price, date=date, title=title, status=status)
            cart3.save()
            cart_of_sender = Cart.objects.all().filter(id=cart2_id)
            cart_of_sender.delete()
            cart2.delete()
            return redirect('fail')

# def reservation(request, cart2_id):
#     cart2 = get_object_or_404(Cart2, order_id=cart2_id)
#     access_token = SocialToken.objects.get(account__user=cart2.sender, account__provider="kakao").token
#     if request.POST['ok']:
#         headers = {
#                     'Authorization': 'Bearer ' + str(access_token)
#                 }
#         receiver_uuids = {
#             "diddnjs02"
#         }
#         title = Food.objects.get(title=cart2.title)
#         image = title.image
#         resAddress = title.author
#         the_address = resAddress.address
#         template_object = { 
#                 "object_type": "location",
#                 "content": {
#                     "title": "카카오 판교오피스",
#                     "description": "카카오 판교오피스 위치입니다.",
#                     "image_url": "https://mud-kage.kakao.com/dn/drTdbB/bWYf06POFPf/owUHIt7K7NoGD0hrzFLeW0/kakaolink40_original.png",
#                     "image_width": 800,
#                     "image_height": 800,
#                     "address": "경기 성남시 분당구 판교역로 235 에이치스퀘어 N동 7층",
#                     "address_title": "카카오 판교오피스",
#                 "link": {
#                 "web_url": "http://dev.kakao.com",
#                 "mobile_web_url": "http://dev.kakao.com/mobile",
#                 "android_execution_params": "platform=android",
#                 "ios_execution_params": "platform=ios"
#                     }
#                 },
#                     {
#                 "buttons": [
#                         "title": "웹으로 보기",
#                         "link": {
#                             "web_url": "http://dev.kakao.com",
#                             "mobile_web_url": "http://dev.kakao.com/mobile"
#                             }
#                     }
#                 ],
#                     }
        
#             URL = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
#             res = requests.post(URL, headers=headers, receiver_uuids=receiver_uuids, template_object=template_object)
#             cart_of_sender = Cart.objects.all().filter(id=cart2_id)
#             cart_of_sender.delete()
#             return redirect('success')
# 
# 
def fail(request):
    return render(request, 'check_fail.html')