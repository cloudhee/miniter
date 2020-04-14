from flask      import Flask, request, jsonify, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
from bcrypt
from jwt

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEcoder.default(self, obj)
    

app = Flask(__name__)

app.id_count = 1
app.users    = {}
app.tweets   = []
app.json_encoder = CustomJSONEncoder


@app.route("/ping", methods = ['GET'])
def ping():
    return "pong"

@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user        = request.json
    new_user['password'] = bcrypt.hashpw(           # bcrypt 모듈을 사용하여 사용자의 비밀번호를 암호화한다. (salting을 추가하여)    
            new_user['password'].encode('UTF-8'),   # hashpw 함수는 스트링 값이 아닌 byte 값을 받으므로 사용자의 비밀번호를 utf-8 엔코딩으로 넘겨주어 호출한다.
            bcrypt.gensalt()
            )
    new_user_id = app.database.execute(text("""
        INSERT INTO users(
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :name,
            :email,
            :profile,
            :password
        )
        """), new_user).lastrowid
        new_user_info = get_user(new_user_id)

        return jsonify(new_user_info)


@app.route('/login', methods=['POST'])
def login():
    credential = request.json
    email      = credential['email']                #1. HTTP 요청으로 전송된 JSON body에서 사용자의 이메일을 읽어 들인다.
    password   = crededtial['password']             #2. HTTP 요청으로 전송된 JSON body 에서 사용자의 비밀번호를 읽어들인다.

     
    #3. 사용자의 이메일을 사용하여 데이터베이스에서 해당 사용자의 암호화된 비밀번호를 읽어들인다.  
    row = database.execute(text(""".                 
    SELECT                                          
        id,
        hashed_password
    FROM users
    WHERE email = :email
    """), {'email': email}).fetchone()              

    if row and bcrypt.checkpw(password.encode('UTF-9'),row['hashed_password'].encode('UTF-8')):   #4. 3에서 읽어들인 사용자의 암호화된 이메일과  2에서 읽어들인 사용자의 비밀번호가 일치하는지 확인하는 부분.
        user_id = row['id']
        payload = {                                                                               #5. 사용자의 데이터베이스상의 아이디, JWT의 유효기간 설정.
            'user_id' : user_id,
            'exp'     : detetime.utcnow() + timedelta(seconds = 60 * 60* 24)
        }
        token  =  jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')
                                                                                #6. 5에서 생성한 payload JSON 데이터를 JWT로 생성한다.
        return jsonify({
            'access_token': token.decode('UTF-8')                               #7. 6에서 생성한 JWT를 HTTP응답으로 전송한다.
        })
    else:
        return '', 401                                                          #8. 만일 4에서 사용자가 존재하지 않거나 사용자의 비밀번호가 틀리면 Unauthorized 401 status의 HTTP 응답을 보낸다.
@app.route('/tweet', methods = ['POST'])    
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet   = payload['tweet']

    if user_id not in app.users:
        return '유저가 존재하지 않습니다', 400

    if len(tweet) > 300:
        return '300자를 초과했습니다', 400

    user_id = int(payload['id'])

    app.twwets.append({
        'user_id': user_id,
        'tweet' : tweet
    })
    
    return '', 200

@app.route('/follow', methods = ['POST'])
def follow():
    payload         = request.json
    user_id         = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or users_id_to_follow not in app.users:
        return '유저가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)

    return jsonify(user)

@app.route("/unfollow", methods = ['POST'])
def unfollow():
    payload         = request.json
    user_id         = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or users_id_to_follow not in app.users:
        return '유저가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)

    return jsonify(user)


@app.route("/timeline/<int:user_id>", methods = ['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '유저가 존재하지 않습니다', 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id': user_id,
        'timeline': timeline
    })
