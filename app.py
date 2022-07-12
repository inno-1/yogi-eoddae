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
client = MongoClient('mongodb+srv://team5:sparta@cluster0.odclv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client['yogi-eoddae']

# [안웅기 ]JWT 토큰을 만들 때 필요한 문자열.
SECRET_KEY = 'TEAMFIVE'

# [양명규] NAVER MAP API 호출 시 필요한 문자열
MAP_CLIENT_ID = 'bb11xjscda'
MAP_CLIENT_SECRET_KEY = '7Jpoj7foQyXXfDXEdUSxlCM2wd9LG5d5WQHbv24k'

# [양명규] 포스트 정렬 타입 리스트 정의
SORT_TYPE = ['date', 'view', 'recommend']

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
        curstatus = 3

    return cur_status, cur_id

# [안웅기] HTML 페이지 렌더링
@app.route('/')
def home():

    postList = list(db.posts.find({}, {"_id":False}))

    cur_status, cur_id = token_request()

    result = {'status': cur_status}
    posts = load_posts()

    if len(posts) > 0:
        result['posts'] = posts
        result['MAP_CLIENT_ID'] = MAP_CLIENT_ID

    headers = {
        "X-NCP-APIGW-API-KEY-ID": MAP_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": MAP_CLIENT_SECRET_KEY
    }

    for post in posts:
        r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={post['location']}",
                         headers=headers)
        response = r.json()

        if response["status"] == "OK":
            if len(response["addresses"]) > 0:
                x = float(response["addresses"][0]["x"])
                y = float(response["addresses"][0]["y"])
                post['point'] = {'x': x, 'y': y}
            else:
                print("좌표를 찾지 못했습니다")

    return render_template('index.html', result=result, postList=postList)

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/posting')
def posting():
    return render_template('posting.html')

@app.route('/detail/<post_id>')
def detail(post_id):
    token_receive = request.cookies.get('mytoken')
    cur_status, cur_user_id = token_request()

    postList = list(db.posts.find({}, {"_id": False}))

    result = {'status' : cur_status, 'user_id' : cur_user_id}
    review_list = list(db.reviews.find({'post_id' : int(post_id)}))
    for review in review_list:
        review['date'] = review['date'].strftime("%Y-%m-%d %H:%M")
        review['_id'] = str(review['_id'])

    return render_template('detail.html', reviews=review_list, result=result, postList=postList)

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
            'exp': datetime.utcnow() + timedelta(seconds=360)
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


# [안웅기] 리뷰 API
# 목록 조회는 페이지 오픈 시에! -> jinja2로

# 리뷰 작성
@app.route('/api/review', methods=['POST'])
def review_post():
    cur_status, cur_user_id = token_request()
    comment_receive = request.form['comment_give']
    doc = {
        'post_id': 1,
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
    review = list(db.reviews.find_one({'_id' : ObjectId(id_receive)}))
    if review:
        db.reviews.delete_one({'_id' : ObjectId(id_receive)})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg' : '실패쓰'})

# 댓글 수
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


def load_posts(type = 'all'):
    if type == 'all':
        return list(db.posts.find({}, {'_id': False}))  # 정렬 없음
    else:
        return list(db.posts.find({}, {'_id': False}).sort(type, pymongo.DESCENDING))  # 최신순

# 타입을 파라미터로 받음 -> date, view, recommend
@app.route('/post/<type>', methods=['GET'])
def all_listing(type):
    if type in SORT_TYPE:
        posts = load_posts(type)
    else:
        posts = load_posts()

    return jsonify({'all_posts': posts})

# 로그인 된 유저 id를 받음
@app.route('/post/<type>/<int:user_id>', methods=['GET'])
def my_listing(type, user_id):
    if type == 'date':
        post = list(db.posts.find({'user_id': user_id}, {'_id': False}).sort('date', pymongo.DESCENDING))    # 최신순
    elif type == 'view':
        post = list(db.posts.find({'user_id': user_id}, {'_id': False}).sort('view', pymongo.DESCENDING))    # 조회수 순
    elif type == 'recommend':
        post = list(db.posts.find({'user_id': user_id}, {'_id': False}).sort('recommend', pymongo.DESCENDING))   # 추천수 순
    else:
        post = list(db.posts.find({'user_id': user_id}, {'_id': False}))  # 정렬 없음
    return jsonify({'all_posts': post})


ACCESS_KEY_ID = 'AKIAXX6AEBP75R7DMAON'      # 액세스 키 (효원 문의)
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

    file = request.files['file_give']

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'post id-{mytime}.{extension}'

    # save_to = f'static/img/{filename}.{extension}'
    # file.save(save_to)

    s3.put_object(
        ACL="public-read",
        Bucket=BUCKET_NAME,
        Body=file,
        Key=filename,
        ContentType=file.content_type)

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])


    post_list= list(db.posts.find({}, {"_id":False}))
    count = len(post_list) + 1

    doc = {
        'id': count,
        'title': title_receive,
        'date': datetime.now(),
        'user_id': payload['id'],
        'content': content_receive,
        'location': location_receive,
        'file': 'https://yogi-eoddae-bucket.s3.ap-northeast-2.amazonaws.com/' + filename,
        'view': 0,
        'recommand': 0

    }
    db.posts.insert_one(doc)
    return jsonify({'msg': '저장 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)