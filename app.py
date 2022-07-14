import boto3
import pymongo
import requests
from bson.objectid import ObjectId
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import jwt
import hashlib

app = Flask(__name__)

# [안웅기] 개인적인 맥 로컬 환경에 DB 접속 오류로 인한 추가
ca = certifi.where()
client = MongoClient('mongodb+srv://team5:sparta@cluster0.odclv.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client['yogi-eoddae']

# [안웅기 ]JWT 토큰을 만들 때 필요한 문자열.
SECRET_KEY = 'TEAMFIVE'

# [양명규] NAVER MAP API 호출 시 필요한 문자열
MAP_CLIENT_ID = 'bb11xjscda'
MAP_CLIENT_SECRET_KEY = '7Jpoj7foQyXXfDXEdUSxlCM2wd9LG5d5WQHbv24k'

# [양명규] 포스트 정렬 타입 리스트 정의
SORT_TYPE = ['date', 'view', 'recommend']

# [양명규] 이미지 저장 서버 주소
AWS_BUCKET_PATH = 'https://yogi-eoddae-bucket.s3.ap-northeast-2.amazonaws.com/'


# [안웅기] 토큰 리퀘스트 요청한 클라이언트의 토큰을 반환
# 첫번째 반환값 int : 1 - 로그인 상태, 2 - 로그인 기한 만료, 3 - 로그인 하지 않은 상태
# 두번째 반환값 str : 로그인 상태일 경우 해당 유저의 아이디를 반환, 아닐 경우 빈칸
def token_request():
    token_receive = request.cookies.get('mytoken')
    cur_status = 0
    cur_id = ''
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        cur_status = 1
        cur_id = payload['id']
    except jwt.ExpiredSignatureError:
        cur_status = 2
    except jwt.exceptions.DecodeError:
        cur_status = 3

    return cur_status, cur_id


# [안웅기] HTML 페이지 렌더링
@app.route('/')
def home():
    cur_status, cur_id = token_request()
    order = request.args.get('orderby')
    mypost = request.args.get('mypost')
    result = {'status': cur_status}

    if order == None:
        order = 'new'
    if mypost == None or cur_status != 1:
        mypost = '0'
    print(mypost)
    post_list = load_posts(order, mypost, cur_id)
    #post_list = list(db.posts.find({}))
    if len(post_list) > 0:
        for post in post_list:
            post['_id'] = str(post['_id'])
    result['posts'] = post_list
    result['order'] = order
    result['mypost'] = mypost
    result['MAP_CLIENT_ID'] = MAP_CLIENT_ID

    return render_template('index.html', result=result)


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/posting')
def posting():
    cur_status, cur_user_id = token_request()
    result = {'status': cur_status}
    return render_template('posting.html', result=result)


@app.route('/detail/<post_id>')
def detail(post_id):
    token_receive = request.cookies.get('mytoken')
    cur_status, cur_user_id = token_request()
    recommend_status = True
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    post['recommend_count'] = len(post['recommend'])
    for recommend_id in post['recommend']:
        if recommend_id == cur_user_id:
            recommend_status = False

    result = {'status': cur_status, 'user_id': cur_user_id, 'recommend_status' : recommend_status}
    review_list = list(db.reviews.find({'post_id': ObjectId(post_id)}))
    for review in review_list:
        review['date'] = review['date'].strftime("%Y-%m-%d %H:%M")
        review['_id'] = str(review['_id'])

    return render_template('detail.html', reviews=review_list, result=result, post=post)

@app.route('/detail/<post_id>/edit')
def edit(post_id):
    cur_status, cur_user_id = token_request()

    post = db.posts.find_one({'_id': ObjectId(post_id)})
    result = {'status': cur_status, 'user_id': cur_user_id, 'post': post}

    return render_template('posting.html', mode='edit', result=result)


# [안웅기] 로그인을 위한 API

# [안웅기] 회원가입 API
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.users.insert_one({'user_id': id_receive, 'user_pw': pw_hash, 'nickname': nickname_receive})

    return jsonify({'result': 'success'})


# [안웅기] 아이디 중복확인
@app.route('/api/register/check-dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    id_receive = request.form['id_give']
    result = db.users.find_one({'user_id': id_receive})
    if result:
        return jsonify({'result': 'exist'})
    else:
        return jsonify({'result': 'success'})


# [안웅기] 로그인 API
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'user_id': id_receive, 'user_pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [안웅기] 현재 로그인 상태 valid 체크
# 로그인이 되어있으면 'result'로 'success'와 'id' 값을 반환
# 안되어 있으면 'result'로 'fail'과 'msg' 값을 반환
@app.route('/api/check', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success', 'id': payload['id']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})


# [안웅기] 추천하기
@app.route('/api/post-recommend', methods=['POST'])
def post_recommend():
    cur_status, cur_user_id = token_request()
    id_receive = request.form['id_give']
    result = db.posts.find_one({'_id': ObjectId(id_receive)})

    if cur_status == 1:
        if cur_user_id in result['recommend']:
            return jsonify({'result': 'fail', 'msg': '이미 추천하셨습니다.'})
        else:
            db.posts.update_one({'_id': ObjectId(id_receive)}, {'$push': {'recommend': cur_user_id}})
            return jsonify({'result': 'success'})
    elif cur_status == 2:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    else:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})

# [안웅기] 추천해제
@app.route('/api/post-recommend', methods=['DELETE'])
def post_unrecommend():
    cur_status, cur_user_id = token_request()
    id_receive = request.form['id_give']
    result = db.posts.find_one({'_id': ObjectId(id_receive)})

    if cur_status == 1:
        if cur_user_id in result['recommend']:
            db.posts.update_one({'_id': ObjectId(id_receive)}, {'$pull': {'recommend': cur_user_id}})
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'fail', 'msg': '이미 추천하셨습니다.'})
    elif cur_status == 2:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    else:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})

# [안웅기] 뷰 수 추
@app.route('/api/post-view', methods=['POST'])
def post_view():
    cur_status, cur_user_id = token_request()
    id_receive = request.form['id_give']
    result = db.posts.find_one({'_id': ObjectId(id_receive)})

    if cur_status == 1:

        db.posts.update_one({'_id': ObjectId(id_receive)}, {'$set': {'view': result['view'] + 1}})
        return jsonify({'result': 'success'})
    elif cur_status == 2:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    else:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})

# [안웅기] 리뷰 API
# 목록 조회는 페이지 오픈 시에! -> jinja2로

# 리뷰 작성
@app.route('/api/review', methods=['POST'])
def review_post():
    cur_status, cur_user_id = token_request()
    comment_receive = request.form['comment_give']
    id_receive = request.form['id_give']
    doc = {
        'post_id': ObjectId(id_receive),
        'user_id': cur_user_id,
        'comment': comment_receive,
        'date': datetime.now()
    }
    if cur_status == 1:
        db.reviews.insert_one(doc)
        return jsonify({'result': 'success'})
    elif cur_status == 2:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    else:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})


@app.route('/api/review', methods=['DELETE'])
def review_delete():
    id_receive = request.form['id_give']
    review = list(db.reviews.find_one({'_id': ObjectId(id_receive)}))
    if review:
        db.reviews.delete_one({'_id': ObjectId(id_receive)})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '실패쓰'})


# 댓글 수정
@app.route('/api/review', methods=['PUT'])
def review_edit():
    id_receive = request.form['id_give']
    comment_receive = request.form['comment_give']
    review = list(db.reviews.find_one({'_id': ObjectId(id_receive)}))
    if review:
        db.reviews.update_one({'_id': ObjectId(id_receive)}, {'$set': {'comment': comment_receive}})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '실패쓰'})


def load_posts(type='new', mypost=0, user_id=''):
    if mypost == '0':
        if type == 'new':
            return list(db.posts.find({}).sort('date', pymongo.DESCENDING))  # 정렬 없음
        else:
            return list(db.posts.find({}).sort(type, pymongo.DESCENDING))  # 최신순
    else:
        return my_listing(type, user_id)

def my_listing(type, user_id):
    if type == 'new':
        post = list(db.posts.find({'user_id': user_id}).sort('date', pymongo.DESCENDING))  # 최신순
    elif type == 'view':
        post = list(db.posts.find({'user_id': user_id}).sort('view', pymongo.DESCENDING))  # 조회수 순
    elif type == 'recommend':
        post = list(db.posts.find({'user_id': user_id}).sort('recommend', pymongo.DESCENDING))  # 추천수 순
    else:
        post = list(db.posts.find({'user_id': user_id}))  # 정렬 없음
    return post
# 타입을 파라미터로 받음 -> date, view, recommend
@app.route('/post/<type>', methods=['GET'])
def all_listing(type):
    if type in SORT_TYPE:
        posts = load_posts(type)
    else:
        posts = load_posts()

    return jsonify({'all_posts': posts})





ACCESS_KEY_ID = 'AKIAXX6AEBP75R7DMAON'  # 액세스 키 (효원 문의)
ACCESS_SECRET_KEY = 'hEaHB+f8yJY7003yn2nT0znN+6/5hnnndvMUh0+p'
BUCKET_NAME = 'yogi-eoddae-bucket'


def s3_connection():
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=ACCESS_SECRET_KEY)
    return s3


s3 = s3_connection()


# 포스팅
@app.route('/api/post', methods=['POST'])
def save_posting():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    location_receive = request.form['location_give']

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    doc = {
        'title': title_receive,
        'date': datetime.now(),
        'user_id': payload['id'],
        'content': content_receive,
        'location': location_receive,
        'view': 0,
        'recommend': []
    }

    # 파일 첨부했을때만 추가
    if len(request.files) > 0:
        file = request.files['file_give']
        extension = file.filename.split('.')[-1]

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

        filename = f'post id-{mytime}.{extension}'

        s3.put_object(
            ACL="public-read",
            Bucket=BUCKET_NAME,
            Body=file,
            Key=filename,
            ContentType=file.content_type)

        doc['file'] = AWS_BUCKET_PATH + filename
        doc['origin_file_name'] = file.filename

    # [양명규] 입력한 주소를 x,y 좌표로 변환
    headers = {
        "X-NCP-APIGW-API-KEY-ID": MAP_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": MAP_CLIENT_SECRET_KEY
    }

    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={location_receive}",
                     headers=headers)
    response = r.json()

    status = True
    fail_msg = '올바른 주소를 입력해주세요.'
    if response["status"] == "OK":
        if len(response["addresses"]) > 0 and response["addresses"][0]["addressElements"][-1]['longName'] != '':
            # 동작구 우편번호 범위 06900 ~ 07074
            postal_code = int(response["addresses"][0]["addressElements"][-1]['longName'])
            if postal_code >= 7074 or postal_code < 6900 :
                status = False
                fail_msg = '동작구에 해당하는 주소를 입력해주세요.'
            else:
                x = float(response["addresses"][0]["x"])
                y = float(response["addresses"][0]["y"])
                doc['point'] = {'x': x, 'y': y}
        else:
            status = False
    else:
        status = False

    if status is False:
        return jsonify({'result': 'fail', 'msg': fail_msg})
    else:
        db.posts.insert_one(doc)
        return jsonify({'result': 'success','msg': '저장 완료!'})


@app.route('/api/post', methods=['DELETE'])
def post_delete():
    id_receive = request.form['id_give']
    post = list(db.posts.find_one({'_id': ObjectId(id_receive)}))
    if post:
        db.posts.delete_one({'_id': ObjectId(id_receive)})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '삭제에 실패하였습니다.'})

@app.route('/api/post', methods=['PUT'])
def post_edit():
    id_receive = request.form['id_give']
    title_receive = request.form['title_give']
    location_receive = request.form['location_give']
    content_receive = request.form['content_give']

    if len(request.files) > 0:
        file_receive = request.files['file_give']

        extension = file_receive.filename.split('.')[-1]

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

        filename = f'post id-{mytime}.{extension}'

        s3.put_object(
            ACL="public-read",
            Bucket=BUCKET_NAME,
            Body=file_receive,
            Key=filename,
            ContentType=file_receive.content_type)

        file = AWS_BUCKET_PATH + filename
        origin_file_name = file_receive.filename
    else:
        file = request.form['file_give']
        origin_file_name = request.form['file_name_give']

    # [양명규] 입력한 주소를 x,y 좌표로 변환
    headers = {
        "X-NCP-APIGW-API-KEY-ID": MAP_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": MAP_CLIENT_SECRET_KEY
    }

    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={location_receive}",
                     headers=headers)
    response = r.json()

    status = True
    fail_msg = '수정에 실패하였습니다.'
    if response["status"] == "OK":
        if len(response["addresses"]) > 0 and response["addresses"][0]["addressElements"][-1]['longName'] != '':
            # 동작구 우편번호 범위 06900 ~ 07074
            postal_code = int(response["addresses"][0]["addressElements"][-1]['longName'])
            if postal_code >= 7074 or postal_code < 6900:
                status = False
                fail_msg = '동작구에 해당하는 주소를 입력해주세요.'
            else:
                x = float(response["addresses"][0]["x"])
                y = float(response["addresses"][0]["y"])
                point = {'x': x, 'y': y}
        else:
            status = False
            fail_msg = '올바른 주소를 입력해주세요.'
    else:
        status = False
        fail_msg = '올바른 주소를 입력해주세요.'

    post = db.posts.find_one({'_id': ObjectId(id_receive)})
    if post is None:
        status = False

    if status is False:
        return jsonify({'result':'fail', 'msg': fail_msg})
    else:
        db.posts.update_one(
            {'_id': ObjectId(id_receive)},
            {'$set': {
                'title': title_receive, 'location': location_receive, 'content': content_receive, 'file': file,
                'origin_file_name': origin_file_name, 'point': point}
            })
        return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
