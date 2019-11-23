from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from . import models
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
# coolsms
import sys
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
# stream
from django.http import HttpResponse

def stream(request):
    # return HttpResponse(
    #     'data: hi\n\n',
    #     content_type='text/event-stream'
    # )
    profile = Profile.objects.get(user=request.user)
    cart2 = Cart2.objects.all().filter(receiver=profile).filter(status="1")

    if cart2:
        return HttpResponse(
            "data: hi\n\n",
            content_type='text/event-stream'
        )
    # else:
    #     return HttpResponse(
    #         "data: bye\n\n",
    #         content_type='text/event-stream'
    #     )


def home(request):
    foods = Food.objects
    food_list = Food.objects.all()
    paginator = Paginator(food_list,4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'home.html', {'foods':foods, 'posts':posts})

def undo(request):
    profile = Profile.objects.all()
    return render(request, 'undo.html', {'Profile':profile})

# 고객의 장바구니
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
def past(request):
    me = Profile.objects.get(user=request.user)
    past = Cart3.objects.all().filter(receiver=me)
    past = past.order_by('-date')
    # 고객등록을 누르면 Customer로 저장 
    if request.method == 'POST':
        sender = User.objects.get(username=request.POST['sender'])
        receiver = Profile.objects.get(user=request.user)
        form = CustomerForm(request.POST)
        customer = Customer(customer=sender, whose=receiver)
        customer.save()
        if form.is_valid():
            cus = form.save(commit=False)
            cus.reason = request.POST['reason']
            cus.others = request.POST['others']
            cus.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'past.html', {'past':past, 'form':form})

# 고객 수정, 관리
def manage(request, customer_id):
    customer_detail = get_object_or_404(Customer, pk=customer_id)
    # 등록을 누르면 
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer_detail)
        if form.is_valid():
            custom = form.save(commit=False)
            custom.whose = Profile.objects.get(user=request.user)
            custom.reason = request.POST['reason']
            custom.customer = User.objects.get(username=customer_detail.customer)
            custom.save()
            return redirect('customer_list', customer_id=customer_id)
    else:
        form = CustomerForm(instance=customer_detail)
        return render(request, 'manage.html', {'form':form, 'customer':customer_detail})

# 고객 등록
def myCustomers(request):
    if request.method == 'POST':
        me = Profile.objects.get(user=request.user)
        the_customer = User.objects.get(username=request.POST['sender'])
        myCustomer = Customer.objects.all().filter(whose=me).filter(customer=the_customer)
        if myCustomer is None:
            form = CustomerForm(request.POST)
            if form.is_valid():
                cus = form.save(commit=False)
                cus.customer = the_customer
                cus.whose = me
                cus.how_many2 = myCustomer.count()
                cus.reason = ''
                cus.others = ''
                cus.save()
            # 저장 다 하면 조회 홈페이지로 돌리기
                return redirect('customer_list')
        else:
            form = CustomerForm()  
            return render(request, 'myCustomers.html', {'form':form})
        
# 고객 조회
def customer_list(request):
    me = Profile.objects.get(user=request.user)
    mycustomers = Customer.objects.all().filter(whose=me)
    return render(request, 'customer_list.html', {'mycustomers':mycustomers})
    
    # how_many는 Cart3의 receiver=me, sender가 customer의 customer의 개수 
    
# 매장이 보는 게시글관리 
def post_retrieve(request):
    the_author = Profile.objects.get(user=request.user)
    post_list = Food.objects.all().filter(author=the_author)
    return render(request, 'myPostList.html', {'post_list':post_list})

# 더보기 
def detail(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    return render(request, 'detail.html', {'food':food_detail})

# 후기
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

# 요청: 장바구니에 담는 과정 
@login_required
def cart(request, food_id):
    food_detail = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        people = request.POST['people']
        total_price = request.POST['total_price']
        sender = request.user
        receiver = food_detail.author
        the_title = Food.objects.get(title=food_detail.title)
        phone = request.POST['phoneNum']
        cart = Cart(sender=request.user, people=people, total_price=total_price, receiver=receiver, title=the_title,phone=phone)
        cart.save()
        return redirect('myCart')
    return render(request, 'detail.html', {'error':'요청실패', 'food':food_detail})


# 결제준비를 마친 고객이 결제 완료되었다는 문구를 보는 페이지 
def successPage(request):
    access_token = SocialToken.objects.get(account__user=request.user, account__provider="kakao").token
    pg_token = request.GET['pg_token']
    # print("@@@@@@@@@@@@@@@@@@@@@@@@ pg_token : {} , ".format(pg_token))
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
    # print("@@@@@@ {} @@@@@@@@@@@ {}".format(res.status_code, cart2.status))
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
        phone = cart_detail.phone
        cart2 = Cart2(sender=sender, receiver=receiver, people=people, total_price=total_price, request_date=request_date, title=title,phone=phone)
        cart2.save()
        # 그럼 이제 cart는 삭제
        cart_detail.delete()
        return redirect('home')
    else:
        return render(request, 'ordering.html', {'cart':cart_detail})

# 매장 글 등록
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


#  매장 글 수정
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


    #홈화면의 서치바    
def search(request):
    search = request.GET['searchkeyword']
    posts = Food.objects.filter(title__icontains=search) | Food.objects.filter(category__icontains=search) | Food.objects.filter(category2__icontains=search) 
    return render(request,'search.html',{'posts':posts})

# 매장이 자기 글 삭제 
def delete(request, food_id):
    deleted_food = get_object_or_404(Food, pk=food_id)
    if request.method == 'POST':
        deleted_food.delete()
        return redirect('myposts')

#고객의 장바구니 --> 고객이 취소하고 돌아가기 누를 때  
def cancel(request, cart_id):
    cancel_cart = get_object_or_404(Cart, pk=cart_id)
    if request.method == 'POST':
        cancel_cart.delete()
        return redirect('myCart')
    

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
    phone_number = request.POST['phoneNumber']
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
    # 받아온 데이터를 Json => Dict으로 바꿈.(파이썬에서 사용 가능하게)
    if res.status_code == 200:
        resp = json.loads(res.text)
        cart2 = Cart2(
            tid=resp['tid'],order_id=partner_order_id,
            sender=request.user, receiver=partner_user_id, people=quantity, 
            total_price=total_amount, request_date=timezone.now(), title=item_name,status="0",phone=phone_number)
        cart2.save()
        cart = Cart.objects.all().filter(sender=request.user).filter(receiver=partner_user_id)
        cart.delete()
        # print("@@@@@@@@@@@ order id = {} , tid = {}".format(partner_order_id , resp['tid']))
        return redirect(resp['next_redirect_pc_url'])
    else:
        return redirect('fail')
 
    # 매장이 거절    
def checkCanceled(request, cart2_id):
    cart2 = get_object_or_404(Cart2, order_id=cart2_id)
    access_token = SocialToken.objects.get(account__user=cart2.sender, account__provider="kakao").token
    if request.method == 'POST':
        # 거절을 누른 경우
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
        return redirect('past')

# 매장이 승인
def checkDone(request, cart2_id):
    cart2_detail = get_object_or_404(Cart2, order_id=cart2_id)
    if request.method == 'POST':
        api_key = "NCSMT6MABSKAUNEP"
        api_secret = "KRXVXII9XJ7NNQ2APASDXT9MEZNGYX1K"
        minute = request.POST['minute']
        
        params = dict()
        params['type'] = 'sms'
        params['to'] = cart2_detail.phone
        params['from'] = '010-3594-0227'
        params['text'] = '[궁동예약]요청이 승인되었습니다. 예상대기시간:' + minute + '분'
        
        cool = Message(api_key, api_secret)
        try:
            response = cool.send(params)
            print("Success Count : %s" % response['success_count'])
            print("Error Count : %s" % response['error_count'])
            print("Group ID : %s" % response['group_id'])

            if "error_list" in response:
                print("Error List : %s" % response['error_list'])

        except CoolsmsException as e:
            print("Error Code : %s" % e.code)
            print("Error Message : %s" % e.msg)

    
        sender = cart2_detail.sender
        receiver = cart2_detail.receiver
        order_id = cart2_detail.order_id
        people = cart2_detail.people
        total_price = cart2_detail.total_price
        date = timezone.now()
        title = cart2_detail.title
        status = '1'
        cart3 = Cart3(sender=sender, receiver=receiver, order_id=order_id, people=people, total_price=total_price, date=date, title=title, status=status)
        cart3.save()
        cart_of_sender = cart2_detail
        cart_of_sender.delete()
        cart2_detail.delete()
        return redirect('past')
    
        sys.exit()
 
def fail(request):
    return render(request, 'check_fail.html')