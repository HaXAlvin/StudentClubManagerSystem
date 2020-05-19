from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
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
    User(1, 'D0745378', '0000'),
    User(2, 'D0746235', '1111'),
]

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'i05c1u6'  # 設定 JWT 密鑰
jwt = JWTManager(app)

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='qwer25604677',  # getpass('pass')
    db='iosclub',
    charset='utf8mb4',
)


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():  # using JWT
    print(request.get_json())
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if (username, password) not in ((u.username, u.password) for u in users):
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/')  # address
def hello_world():
    return render_template('index.html')


@app.route('/searchName', methods=['POST'])  # API
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
def search():
    return render_template('search.html')


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動
