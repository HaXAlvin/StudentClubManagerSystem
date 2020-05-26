import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect
import flask_jwt_extended as jwt
import pyqrcode
import hashlib
import pymysql
import pandas
from bs4 import BeautifulSoup
import random
import string


class User(object):
    def __init__(self, userID, username, password):
        self.userID = userID
        self.username = username
        self.password = password

    def __str__(self):
        return "User(userID='%s')" % self.userID


# f = open("/userList.json", mode="a")
# f = open("/userList.json", mode="r")
# with open('userList.json' , 'r') as reader:
#     jf = json.loads(reader.read())
users = [
    User('D0745378', '薛竣祐', '0000'),
    User('D0746235', '黃傳霖', '1111'),
]
app = Flask(__name__)

s = hashlib.sha256()
s.update("i05c1u652005505".encode('utf-8'))
key = s.hexdigest()
print('key:', key)
app.config['JWT_SECRET_KEY'] = key  # set jwt key
app.config['JWT_TOKEN_LOCATION'] = 'cookies'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=300)  # 逾期時間
app.config['JWT_ALGORITHM'] = 'HS256'  # hash type
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'  # cookie name
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(seconds=300)
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
jwtAPP = jwt.JWTManager(app)

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='qwer25604677',  # getpass('pass')
    db='iosclub',
    charset='utf8mb4',
)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    print(request.get_json())
    if not request.is_json:
        return jsonify({"login": False, "msg": "Missing JSON in request"}), 400
    account = request.json.get('account', None)
    password = request.json.get('password', None)
    if not account:
        return jsonify({"login": False, "msg": "Missing account parameter"}), 400
    if not password:
        return jsonify({"login": False, "msg": "Missing password parameter"}), 400
    if (account, password) not in ((u.userID, u.password) for u in users):
        return jsonify({"login": False, "msg": "Bad account or password"}), 401
    access_token = jwt.create_access_token(
        identity={
            'account': account
        },
        headers={
            "typ": "JWT",
            "alg": "HS256"
        }
    )
    refresh_token = jwt.create_refresh_token(
        identity={
            'account': account
        },
        headers={
            "typ": "JWT",
            "alg": "HS256"
        }
    )
    next_page = request.json.get('next', None)
    url = '/'
    if next_page:
        next_page.replace('%2F', '/')
        url = next_page
    resp = jsonify({'login': True, 'next': url})
    # resp = redirect(url_for('index'), 302)
    jwt.set_access_cookies(resp, access_token)
    jwt.set_refresh_cookies(resp, refresh_token)
    return resp


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
@jwt.jwt_optional
def index():
    identity = jwt.get_jwt_identity()
    print('index identity:', identity)
    if identity is None:
        # print('no')
        resp = redirect(url_for('login', next=request.endpoint, _method='GET'))
        # resp.set_cookie(key='pre', value='index')
        return resp
    return render_template('index.html', account=identity['account'])


@jwtAPP.expired_token_loader  # 逾期func
def my_expired():
    resp = redirect(url_for('login'))
    jwt.unset_jwt_cookies(resp)
    return resp, 302


@app.route('/searchName', methods=['POST'])
def search_name():
    conn.ping(reconnect=True)
    res = {'result': 'no'}
    with conn.cursor() as cursor:
        name = request.json.get('data', None)
        sql = "SELECT * FROM memberList WHERE member_name = %s;"
        cursor.execute(sql, name)
        results = cursor.fetchall()
        if not results:
            res['result'] = 'No data found'
        else:
            df = pandas.DataFrame(list(results), columns=[i[0] for i in cursor.description])  # make a frame
            soup = BeautifulSoup(df.to_html(), 'html.parser')  # turn into html table
            soup.find('table')['class'] = 'table'  # edit html
            res['result'] = soup.prettify()  # turn soup object to str
    return jsonify(res)  # 回傳json格式


@app.route('/query', methods=['POST'])
def query():
    conn.ping(reconnect=True)
    res = {'result': 'no'}
    try:
        with conn.cursor() as cursor:
            cursor.execute(request.json.get('data', None))
            conn.commit()
            results = cursor.fetchall()
            print(results)
            if not results:
                res['result'] = 'Success'
            else:
                df = pandas.DataFrame(list(results), columns=[i[0] for i in cursor.description])  # make a frame
                soup = BeautifulSoup(df.to_html(), 'html.parser')  # turn into html table
                soup.find('table')['class'] = 'table'  # edit html
                res['result'] = soup.prettify()  # turn soup object to str
    except Exception as error_message:
        conn.ping(reconnect=True)  # true = reconnect
        res['result'] = str(error_message)
    return jsonify(res)  # 回傳json格式


@app.route('/search', methods=['GET'])
@jwt.jwt_optional
def search():
    identity = jwt.get_jwt_identity()
    print('search identity:', identity)
    if identity is None:
        redirect(url_for('login'))
    return render_template('search.html')


@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('sign_up.html')


punch_record = []


@app.route('/creat_qrcode', methods=['GET'])
def creat_qrcode():
    letters = string.ascii_letters
    code = ''.join(random.choice(letters) for _ in range(10))
    record = {'code': code, 'expired': datetime.datetime.now() + datetime.timedelta(minutes=3)}
    punch_record.append(record)
    url = '/punch_in/{}'.format(code)
    qrcode = pyqrcode.create('127.0.0.1{}'.format(url), error='H')
    image_as_str = qrcode.png_as_base64_str(scale=15)
    return render_template('qrcode.html', qrcode=image_as_str, url=url)


@app.route('/punch_in/<code>')
@jwt.jwt_optional
def punch_in(code):
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next=request.endpoint+'/'+code))
    for record in punch_record:
        if code == record['code']:
            if datetime.datetime.now() <= record['expired']:
                print(identity['account'], 'punch in success')
                punch_record.remove(record)
                return jsonify({'punch_in': True})
            else:
                print('datetime expired')
                return jsonify({'punch_in': False})
    return jsonify({'punch_in': False})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動


# CSRF refresh
# @app.route('/refresh', methods=['POST'])
# @jwt_refresh_token_required
# def refresh():
#     # verify_jwt_refresh_token_in_request()
#     print(1111111111111111111111111111111)
#     identity = get_jwt_identity()
#     print(identity)
#     resp = jsonify({'login': True})
#     new_token = create_access_token(
#         identity={
#             'account': identity['account']
#         },
#         headers={
#             "typ": "JWT",
#             "alg": "HS256"
#         }
#     )
#     set_access_cookies(resp, new_token)
#     return jsonify(resp), 200
