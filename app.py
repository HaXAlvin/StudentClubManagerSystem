import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_jwt_extended import get_jwt_identity, JWTManager, create_access_token, jwt_optional, set_access_cookies
import hashlib
import pymysql
import pandas
from bs4 import BeautifulSoup


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
s.update("i05c1u6".encode('utf-8'))
key = s.hexdigest()
print('key:', key)
app.config['JWT_SECRET_KEY'] = key  # set jwt key
app.config['JWT_TOKEN_LOCATION'] = 'cookies'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=600)  # 逾期時間
app.config['JWT_ALGORITHM'] = 'HS256'  # hash type
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'  # cookie name
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
jwtAPP = JWTManager(app)

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='0000',  # getpass('pass')
    db='iosclub',
    charset='utf8mb4',
)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/loginAccount', methods=['POST'])
def loginAccount():  # using JWT
    print(request.get_json())
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    account = request.json.get('account', None)
    password = request.json.get('password', None)
    if not account:
        return jsonify({"msg": "Missing account parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if (account, password) not in ((u.userID, u.password) for u in users):
        return jsonify({"msg": "Bad account or password"}), 401
    token = create_access_token(
        identity={
            'account': account
        },
        headers={
            "typ": "JWT",
            "alg": "HS256"
        }
    )
    resp = jsonify({'login': True})
    set_access_cookies(resp, token)
    return resp, 200


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
@jwt_optional
def index():
    identity = get_jwt_identity()
    print('index identity:', identity)

    # verify_jwt_in_request_optional()
    if identity is None:
        return redirect(url_for('login'))
    return render_template('index.html', account=identity['account'])


@jwtAPP.expired_token_loader  # 逾期func
def my_expired():
    resp = redirect(url_for('login'))
    resp.set_cookie('access_token_cookie', "")
    return resp


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
@jwt_optional
def search():
    identity = get_jwt_identity()
    print('search identity:', identity)
    if identity is None:
        return render_template('login.html')
    return render_template('search.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動
