import base64
from datetime import timedelta, datetime
import os
from PIL import Image
from flask import Flask, render_template, request, jsonify, url_for, redirect
import flask_jwt_extended as jwt
import pyqrcode
import hashlib
import pymysql
import pandas
from bs4 import BeautifulSoup
from random import choice
from string import ascii_letters
from time import sleep
import threading
from io import BytesIO


class User(object):
    def __init__(self, userNID, username, password, manager):
        self.userNID = userNID
        self.username = username
        self.password = password
        self.manager = manager


class Config(object):
    # app set
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = '5277'
    # jwt set
    JWT_SECRET_KEY = hashlib.sha256("i05c1u652005505".encode('utf-8')).hexdigest()
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=300)  # 逾期時間
    JWT_ALGORITHM = 'HS256'  # hash type
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'  # cookie name
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=300)
    JWT_ACCESS_COOKIE_PATH = '/'
    # db set
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PWD = '0000'
    DB_NAME = 'iosclub'
    DB_CHARSET = 'utf8mb4'
    # qrcode set
    QRCODE_LEN = 10
    QRCODE_EXPIRED = timedelta(minutes=3)
    # other set
    CLEAN_RECORD_DELAY = 3600


# f = open("/userList.json", mode="a")
# f = open("/userList.json", mode="r")
# with open('userList.json' , 'r') as reader:
#     jf = json.loads(reader.read())
app = Flask(__name__)
app.config.from_object(Config)  # get setting
jwtAPP = jwt.JWTManager(app)
punch_record = []
img_path = os.path.dirname(os.path.abspath(__file__))+r'\static\img'
logos = [Image.open(img_path + fr'\icon0{i}.png') for i in range(1, 5)]

users = {
    1: User('D0745378', '薛竣祐', '0000', True),
    2: User('D0746235', '黃傳霖', '1111', True),
    3: User('D0000000', '劉祐炘', '6666', False)
}
# print('key:', app.config['JWT_SECRET_KEY'])
while True:
    try:
        conn = pymysql.connect(
            host=app.config.get('HOST'),
            port=app.config.get('DB_PORT'),
            user=app.config.get('DB_USER'),
            passwd=app.config.get('DB_PWD'),
            db=app.config.get('DB_NAME'),
            charset=app.config.get('DB_CHARSET'),
        )
        break
    except pymysql.err.OperationalError as msg:
        print(f'**{msg}**')
        sleep(1)


def jwt_creat_token(types, account):
    method = {'access': jwt.create_access_token, 'refresh': jwt.create_refresh_token}
    token = method[types](
        identity={'account': account},
        headers={"typ": "JWT", "alg": "HS256"}
    )
    return token


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
    if (account, password) not in ((u.userNID, u.password) for u in users.values()):
        return jsonify({"login": False, "msg": "Bad account or password"}), 401
    access_token = jwt_creat_token('access', account)
    refresh_token = jwt_creat_token('refresh', account)
    next_page = request.json.get('next', None)
    if next_page == "":
        next_page = '/'
    next_page.replace('%2F', '/')
    print(next_page)
    resp = jsonify({'login': True, 'next': next_page})
    # resp = redirect(url, code=302)
    jwt.set_access_cookies(resp, access_token)
    jwt.set_refresh_cookies(resp, refresh_token)
    return resp


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
@jwt.jwt_optional
def index():
    identity = jwt.get_jwt_identity()
    if identity is None:
        print('index identity:', identity)
        resp = redirect(url_for('login', next=request.endpoint, _method='GET'))
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


@app.route('/creat_qrcode', methods=['GET'])
@jwt.jwt_optional
def creat_qrcode():
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next=request.endpoint))
    accept = False
    for user in users.values():
        print(user.userNID, identity['account'], user.manager)
        if user.userNID == identity['account'] and user.manager is True:
            accept = True
            break
    if accept is False:
        return redirect(url_for('index'))
    letters = ascii_letters
    code = ''.join(choice(letters) for _ in range(app.config.get('QRCODE_LEN')))
    record = {'code': code, 'expired': datetime.now() + app.config.get('QRCODE_EXPIRED')}
    punch_record.append(record)
    url = f'/punch_in/{code}'
    qrcode = pyqrcode.create(f'{app.config.get("HOST")}:{app.config.get("PORT")}{url}', error='H')
    qrcode.png(img_path + r'\qrcode.png', scale=14)
    img = Image.open(img_path+r'\qrcode.png')
    img = img.convert("RGBA")
    img_size = img.width
    icon_size = (img_size**2*0.08)**0.5
    logo = choice(logos)
    shapes = [int(img_size/2-icon_size/2) if i < 2 else int(img_size/2+icon_size/2) for i in range(4)]
    img.crop(shapes)
    logo = logo.resize((shapes[2] - shapes[0], shapes[3] - shapes[1]))
    logo.convert('RGBA')
    # mask = Image.new("L", logo.size, 0)
    # mask_im_blur = mask.filter(ImageFilter.GaussianBlur(10))
    # draw = ImageDraw.Draw(mask)
    # print(mask.size)
    # draw.ellipse((0, 0, mask.width, mask.width), fill=255)
    # mask.show()
    # img.paste(mask_im_blur, shapes)
    img.paste(logo, shapes, logo)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return render_template('qrcode.html', qrcode=img_str, url=url)


@app.route('/punch_in/<code>')
@jwt.jwt_optional
def punch_in(code):
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next=request.endpoint+'/'+code))
    for record in punch_record:
        if code == record['code']:
            if datetime.now() <= record['expired']:
                # print(identity['account'], 'punch in success')
                punch_record.remove(record)
                punch_in_sql(identity['account'])
                return jsonify({'punch_in': True})
            else:
                print('datetime expired')
                return jsonify({'punch_in': False})
    return jsonify({'punch_in': False})


def punch_in_sql(account):
    conn.ping(reconnect=True)
    try:
        with conn.cursor() as cursor:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into class_state(member_id, date, attendance, register) " \
                  "values((select member_id from memberlist where member_nid = %s), %s, 1, 1);"
            cursor.execute(sql, (account, now))
            conn.commit()
            results = cursor.fetchall()
            if not results:
                print(account, 'punch in at ', now, 'success')
    except pymysql.err.OperationalError as e:
        print(e)


def clean_record():  # clean qrcode list every specific time
    while True:
        print("**Start Clean**")
        now_time = datetime.now()
        for records in punch_record:
            if records['expired'] > now_time:
                print("**Clean 1 record**")
                punch_record.remove(records)
        print("**Ended Clean**")
        sleep(app.config.get('CLEAN_RECORD_DELAY'))


clean_record_thread = threading.Thread(target=clean_record)
clean_record_thread.start()


if __name__ == '__main__':
    app.run(port=app.config.get('PORT'), host=app.config.get('HOST'))


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
