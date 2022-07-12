import pymongo
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import certifi
import jwt
import datetime
import hashlib
app = Flask(__name__)

# [안웅기] 개인적인 맥 로컬 환경에 DB 접속 오류로 인한 추가
ca = certifi.where()
client = MongoClient('mongodb+srv://team5:sparta@cluster0.odclv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client['yogi-eoddae']

# [안웅기 ]JWT 토큰을 만들 때 필요한 문자열.
SECRET_KEY = 'TEAMFIVE'

# [안웅기] HTML 페이지 렌더링
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    curstatus = 0
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        curstatus = 1
    except jwt.ExpiredSignatureError:
        curstatus = 0
        #return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        curstatus = 0
        #return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    return render_template('index.html', status=curstatus)

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

@app.route('/detail')
def detail():
    return render_template('detail.html')

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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=360)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/api/check', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return jsonify({'result': 'success'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 하세요.'})


# 타입을 파라미터로 받음 -> date, view, recommend
@app.route('/post/<type>', methods=['GET'])
def all_listing(type):
    if type == 'date':
        post = list(db.posts.find({}, {'_id': False}).sort('date', pymongo.DESCENDING))    # 최신순
    elif type == 'view':
        post = list(db.posts.find({}, {'_id': False}).sort('view', pymongo.DESCENDING))    # 조회수 순
    elif type == 'recommend':
        post = list(db.posts.find({}, {'_id': False}).sort('recommend', pymongo.DESCENDING))   # 추천수 순
    else:
        post = list(db.posts.find({}, {'_id': False}))  # 정렬 없음
    return jsonify({'all_posts': post})


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

@app.route('/api/post', methods=['POST'])
def save_posting ():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    location_receive = request.form['location_give']

    file = request.files['file_give']

    extension = file.filename.split('.')[-1]

    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/img/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'title': title_receive,
        'content': content_receive,
        'location': location_receive,
        'file': f'{filename}.{extension}'
    }

    db.posts.insert_one(doc)
    return jsonify({'msg': '저장 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)