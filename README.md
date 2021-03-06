# (가제) 궁동예약

## 코드를 만지게 된 계기
- "작동"에만 집중했던 프로젝트라 함수의 위치나 코드 등 퀄리티가 매우 낮다. 
- 리팩토링의 필요성 + 더 발전시키고 싶은 욕심에서 시작했다. 
- 배우고 싶었던 기술도 접목시켜서 공부할 겸 시작했다. 

## 바꿀 것들 
> 2020-12-01 오후 11:26 기준
1. 모델 
   - 카테고리를 너무 세부적으로 나눈 것 같은 느낌이 든다. 
   - 배민 앱을 참고하면서 다시 짜면 좋을 것 같다. 
2. 섬네일
   - 너무.. 정리가 안되어있었다 ㅠㅠ
3. 지도 
   - 주소 입력할 때 지도를 가져오면 좋을 것 같다.  

> 2020-11-27 오전 12시 기준
1. 제목 
   - 진짜 꼭 바꿀거다. 
2. 디자인 
   - UX를 좀 더 생각한 디자인으로 바꾸고 싶다. 
   - 반응형으로 만들 예정 
3. 앱 분할
   - 사실 food라는 app 안에 거의 모든 기능을 구현했었다. 
   - 이를 기능별 혹은 유저특성별로 나눌 예정
   - 코드 재사용성, 리팩토링 등을 통해 코드 퀄리티를 좀 더 높일 예정 

## 바꾼 것들 
> 2020-12-01 오후 11:26 기준 
1. [x] urls 수정하기 
   - 기존 url 이름은 알아듣기 어렵게 지어놔서(..) 좀 길더라도 알아보기 쉽게 바꿨다. 
   - 각각 html파일과 views.py에 잘 매칭해줬다. 
   - runserver로 열면서 그때그때 난 오류들의 경우 닥치는대로 고쳐줬는데, 전반적으로 posts에 해당하는 부분들 위주로 수정했다. 

2. [x] js 파일 두기 
   - 기존에는 html 파일안에 js를 넣었다. 
   - static 파일로 저장해서 loadstatic하여 js코드를 연결했다. 
   - 각 기능마다 다른 파일을 만들어서 재활용성을 높이고자 했다. 
     - 그러다 search 기능을 아예 base로 빼버리는게 좋겠다는 생각이 들어서 이 부분 수정할 예정 

3. [x] js 코드 정리 
   - 서버에서 불러오는 데이터값의 경우 `textContent`를 사용해서 해당 데이터를 가져왔다.
   - 특이점은...
     - detail 페이지에서 요청하기 버튼을 누르면 그때 alert창이 떠야하는데
     - 자꾸 새로고침 할때마다 요청하기 버튼이 나왔다. 
     - 분명 코드상으로 보면 사용자가 버튼을 눌러야하는데.. 분명 누르지않아도 버튼이 클릭된것처럼 로드되는것 같았다. 
     - 그래서...
       1. 처음에 넣어줬던 defer를 뺐다. 
       2. 의미 없었다. 
       3. js에서 버튼을 가져올 때 let 변수안에 넣어줬는데, const로 바꾸었다. 
       4. 근데 됐다...?
     - 이 부분에 대한 공부가 좀 필요할 것 같다.

> 2020-11-27 오전 12시 기준
1. [x] 앱 분할 
  - food는 
    - posts : 게시글 관련
    - carts 
      - customer: 예약 요청, 예약 성공, 예약 실패 등 "고객" 관련 요청에 대한 것들
      - restaurants: 예약 승인, 예약 거절, 예약 관리, 고객관리 등 "사업자" 관련 요청에 대한 것들
      - carts라고 정한 이유는 쇼핑몰의 장바구니랑 비슷한 기능 같아서 붙였으나 더 좋은 이름이 생각나면 바꿀수도!
    - home
  - 으로 나뉘었다. 

2. [x] views, urls, models 정리 
   - 함수 명을 (길더라도) 알아보기 쉽게 바꾸었다.
   - html 파일명도 (길더라도) 알아보기 쉽게 바꾸었다. 
   - 각 앱에 적합한 모델들을 제자리에 위치시켰다. 
   - 각 앱에 urls.py를 만들었다. 
   - 전체 urls.py에는 includes를 사용하여 각 앱의 url들을 불러오도록 하였다. 

## 패키지
- django-allauth : 소셜로그인 관련
- psycopg2 : postgresQL 관련
- django-ckeditor : 글쓰기 에디터 관련
- django_grip
- whitenoise
- django-crispy-forms
- PIL (for image file)
