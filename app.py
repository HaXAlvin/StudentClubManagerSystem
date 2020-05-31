from base64 import b64encode
from datetime import timedelta, datetime
from os import path
from PIL import Image
from flask import Flask, render_template, request, jsonify, url_for, redirect
import flask_jwt_extended as jwt
from flask_apscheduler import APScheduler
import pyqrcode
from hashlib import sha256
import pymysql
from pandas import DataFrame
from bs4 import BeautifulSoup
from random import choice
from string import ascii_letters
from time import sleep
from io import BytesIO


class User(object):
    def __init__(self, userNID, username, password, manager):
        self.userNID = userNID
        self.username = username
        self.password = password
        self.manager = manager


class Config:
    # app set
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = '5277'
    # jwt set
    JWT_SECRET_KEY = sha256("i05c1u652005505".encode('utf-8')).hexdigest()
    JWT_TOKEN_LOCATION = 'cookies'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10)  # 逾期時間
    JWT_ALGORITHM = 'HS256'  # hash type
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'  # cookie name
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)
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
    JOBS = [
        {
            'id': 'clean_record',
            'func': '__main__:clean_record',
            'trigger': {
                'type': 'interval',
                'seconds': 3600  # clean timedelta
            }
        }
    ]


# f = open("/userList.json", mode="a")
# f = open("/userList.json", mode="r")
# with open('userList.json' , 'r') as reader:
#     jf = json.loads(reader.read())
app = Flask(__name__)
app.config.from_object(Config())  # get setting
jwtAPP = jwt.JWTManager(app)
punch_record = []
img_path = path.dirname(path.abspath(__file__)) + '/static/img'
logos = [Image.open(img_path + f'/icon0{i}.png') for i in range(1, 5)]
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


def jwt_create_token(types, account):
    method = {'access': jwt.create_access_token, 'refresh': jwt.create_refresh_token}
    return method[types](identity={'account': account}, headers={"typ": "JWT", "alg": "HS256"})


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
    access_token = jwt_create_token('access', account)
    refresh_token = jwt_create_token('refresh', account)
    next_page = request.json.get('next', None).replace('%2F', '/')
    if next_page == "":
        next_page = '/'
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
    print('index identity:', identity)
    if identity is None:
        resp = redirect(url_for('login', next='/'))
        return resp
    return render_template('index.html', account=identity['account'])


@jwtAPP.expired_token_loader  # 逾期func
def my_expired():
    # print(request.path)
    resp = redirect(url_for('login', next=request.path))
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
        print(results)
        if not results:
            res['result'] = 'No data found'
        else:
            df = DataFrame(list(results), columns=[i[0] for i in cursor.description])  # make a frame
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
                df = DataFrame(list(results), columns=[i[0] for i in cursor.description])  # make a frame
                soup = BeautifulSoup(df.to_html(), 'html.parser')  # turn into html table
                soup.find('table')['class'] = 'table'  # edit html
                res['result'] = soup.prettify()  # turn soup object to str
    except Exception as error_message:
        res['result'] = str(error_message)
    return jsonify(res)  # 回傳json格式


@app.route('/search', methods=['GET'])
@jwt.jwt_optional
def search():
    identity = jwt.get_jwt_identity()
    print('search identity:', identity)
    if identity is None:
        redirect(url_for('login', next='/search'))
    return render_template('search.html')


@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('sign_up.html')


@app.route('/create_qrcode', methods=['GET'])
@jwt.jwt_optional
def create_qrcode():
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next='create_qrcode'))
    accept = False
    for user in users.values():
        print(user.userNID, identity['account'], user.manager)
        if user.userNID == identity['account'] and user.manager is True:
            accept = True
            break
    if accept is False:
        return redirect(url_for('index'))
    code = ''.join(choice(ascii_letters) for _ in range(app.config.get('QRCODE_LEN')))
    record = {'code': code, 'expired': datetime.now() + app.config.get('QRCODE_EXPIRED')}
    punch_record.append(record)
    url = f'/punch_in/{code}'
    qrcode = pyqrcode.create(f'{app.config.get("HOST")}:{app.config.get("PORT")}{url}', error='H')
    qrcode.png(img_path + '/qrcode.png', scale=14)  # 33*14
    img = Image.open(img_path + '/qrcode.png')
    img = img.convert("RGBA")
    img_size = img.width
    icon_size = (img_size ** 2 * 0.08) ** 0.5
    shapes = [int(img_size / 2 - icon_size / 2) if i < 2 else int(img_size / 2 + icon_size / 2) for i in range(4)]
    img.crop(shapes)
    logo = choice(logos)
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
    img_str = b64encode(buffered.getvalue()).decode()
    return render_template('qrcode.html', qrcode=img_str, url=url)


@app.route('/punch_in/<code>')
@jwt.jwt_optional
def punch_in(code):
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next='/punch_in/' + code))
    for record in punch_record:
        if code == record['code']:
            if datetime.now() <= record['expired']:
                punch_record.remove(record)
                return jsonify({'punch_in': punch_in_sql(identity['account'])})
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
            results = cursor.fetchall()
            if not results:
                conn.commit()
                print(account, 'punch in at ', now, 'success')
                return True
            else:
                return False
    except pymysql.err.OperationalError as e:
        print(e)
        return False


@app.route('/punch_list', methods=['GET'])
@jwt.jwt_optional
def punch_list():
    conn.ping(reconnect=True)
    identity = jwt.get_jwt_identity()
    if identity is None:
        return redirect(url_for('login', next='/punch_list'))
    try:
        with conn.cursor() as cursor:
            already = "select date from class_state where member_id = " \
                      "(select member_id from memberlist where member_nid = %s);"
            cursor.execute(already, identity['account'])
            return jsonify({'msg': 'success', 'res': cursor.fetchall()})
    except pymysql.err.OperationalError as e:
        print(e)
        return jsonify({'msg': e})


@app.route('/attendance', methods=['GET'])
def attendance():
    conn.ping(reconnect=True)
    member_id = []
    member_name = []
    try:
        with conn.cursor() as cursor:
            sql = "SELECT member_id,member_name FROM memberlist;"
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                member_id.append(row[0])
                member_name.append(row[1])
            sql = "SELECT * FROM class_state;"
            cursor.execute(sql)
            results = cursor.fetchall()
    except pymysql.err.OperationalError as e:
        print(e)
        return e
    data = {
        'id': member_id,
        'name': member_name
    }
    for row in results:
        row_date = row[2].strftime("%Y-%m-%d")
        if row_date not in data.keys():
            data[row_date] = ["-" for _ in range(len(member_id))]
        update_index = data['id'].index(row[1])
        if (row[3], row[4]) in [(1, 1), (1, 0)]:
            data[row_date][update_index] = 'O'
        elif (row[3], row[4]) == (0, 1):
            data[row_date][update_index] = 'LEAVE'
        else:
            data[row_date][update_index] = '-'
    dataFrame = DataFrame(data)
    soup = BeautifulSoup(dataFrame.to_html(), 'html.parser')  # turn into html table
    # soup.find('table')['class'] = 'table'  # edit html
    return soup.prettify()


def clean_record():  # clean qrcode list every specific time
    now_time = datetime.now()
    print(f"**Start Clean at {now_time}**")
    for records in punch_record:
        if records['expired'] > now_time:
            print("**Clean 1 record**")
            punch_record.remove(records)
    now_time = datetime.now()
    print(f"**Ended Clean at {now_time}**")


if __name__ == '__main__':
    scheduler = APScheduler()  # 例項化APScheduler
    scheduler.init_app(app)  # 把任務列表放進flask
    scheduler.start()  # 啟動任務列表
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
