from flask import Flask,render_template,request,redirect,url_for,jsonify
from flask_socketio import SocketIO,send
import json,os,base64
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import pymysql
import random, string
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ongoogray!'
socketio = SocketIO(app)

conn = pymysql.connect(
    host = '192.168.1.6',
    user = 'root',
    passwd = 'ongoogray',
    db = 'mydondon'
)
user = {}
clients = []
login_cookie = {}
def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def PathGetImageStr(p):
    img_str = ""
    with open(p, "rb") as imageFile:
        img_str = base64.b64encode(imageFile.read())
    return img_str.decode('utf-8')
def appGetAllOrder(csn,isdeal,output):
    timelink = []
    with conn.cursor() as cursor:
        sql2 = 'select Time from order_list,deal where CN= %s and O_ID = order_id group by Time order by Time desc'
        sql = 'select Time from order_list where CN = %s AND order_id not in  ( select order_id from order_list,deal  where Order_id = O_ID ) group by time order by time desc'
        val = (csn)
        if isdeal == 0:  # 未處理
            cursor.execute(sql, val)
        else:
            cursor.execute(sql2, val)
        results = cursor.fetchall()
        for i in results:
            timelink.append(str(i[0]))
    for i in timelink:
        a = {'time': i, 'isdeal': isdeal}
        with conn.cursor() as cursor:
            sql = 'select Food_ID,Fname,o.Number,Price from food_list,order_list as o where CN = %s and Time = %s and Food_ID = fid'
            val = (csn, i)
            cursor.execute(sql, val)
            results = cursor.fetchall()
            b = []
            for j in results:
                b.append({'foodid': j[0], 'foodname': j[1], 'foodnumber': j[2],'foodprice':j[3]})
            a['foodlist'] = b
        output.append(a)





@app.route('/')
def hello_world(name=None):
    return render_template('hello.html',name=name,text="你好")
@app.route('/yh')
def XD(name=None):
    return render_template('XD.html',name=name,text="你好")

@app.route('/login', methods=['POST'])
def login():
    response = redirect(url_for('ManagePage'))
    with conn.cursor() as cursor:
        username = request.form['username']
        password = request.form['password']
        sql = 'select * from Employee Where Acc = %s and Psw = %s'
        val = (username, password)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        conn.commit()
        if results != ():
            ssn = results[0][0]
            cookie_string = randomword(20)
            if ssn in user:
                login_cookie.pop(user[ssn]['SessionSSN'])
            user[ssn] = {'SessionSSN':cookie_string}
            login_cookie[cookie_string] = {'userssn':ssn}
            response.set_cookie('SessionSSN', cookie_string)
        else:
            response = redirect(url_for('hello_world'))
    return response
@app.route('/ManagePage', methods=['GET'])
def ManagePage():

    cookie = request.cookies.get('SessionSSN')

    if cookie in login_cookie:
        return render_template('ManagePage1.html')
    else:
        return redirect(url_for('hello_world'))

@app.route('/getOrderDetail', methods=['POST'])
def getOrderDetail():
    res = {'result': 'no'}
    t = request.form['time'].replace('\n    ','')
    cn = int(request.form['cn'])
    with conn.cursor() as cursor:
        sql = 'select Time,Order_id, CN,Fname ,o.Number from order_list as o,food_list where cn = %s and time = %s and Food_id = fid'
        val = (cn, t)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        df = pd.DataFrame(list(results), columns=[i[0] for i in cursor.description])
        soup = BeautifulSoup(df.to_html(), 'html.parser')
        soup.find('table')['class'] = 'table table-striped table-dark'
        soup.find('table')['border'] = 0
        soup.find('tr')['style'] = ''
        res['result'] = soup.prettify()
    return jsonify(res)
@app.route('/addDeal', methods=['POST'])
def addDeal():
    SessionSSN = request.cookies.get('SessionSSN')
    if SessionSSN not in login_cookie:
        print('addDeal no token')
        return "no"
    ssn = login_cookie[SessionSSN]['userssn']
    t = request.form['time'].replace('\n    ', '')
    cn = int(request.form['cn'])
    dnow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders = []
    with conn.cursor() as cursor:
        sql = 'select Order_id from order_list where cn = %s and time = %s'
        val = (cn, t)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        for i in results:
            orders.append(i[0])
    with conn.cursor() as cursor:
        sql = "insert into Deal (SSN,Deal_time,O_ID) values (%s,%s,%s)"
        val = [(ssn,dnow,i) for i in orders]
        cursor.executemany(sql,val)
        conn.commit()
    return "ok"
@app.route('/searchSQL', methods=['POST'])
def searchSQL():
    res = {'result': 'no'}
    sql = request.form['value']
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.commit()
            if list(results) == []:
                res['result'] = 'success but no data!'
            else:
                df = pd.DataFrame(list(results), columns=[i[0] for i in cursor.description])
                soup = BeautifulSoup(df.to_html(), 'html.parser')
                soup.find('table')['class'] = 'table table-hover'
                soup.find('table')['border'] = 0
                soup.find('tr')['style'] = ''
                res = {'result':soup.prettify()}
    except Exception as e:
        res['result'] = str(e)
    return jsonify(res)

@app.route('/Logout', methods=['POST'])
def Logout():
    print(request.form['SessionSSN'])
    return redirect(url_for('hello_world'))
@app.route('/testSocket', methods=['POST'])
def test():
    data = request.form['data']
    print(request.form['data'])
    #socketio.emit('message',{'data':request.form['data']})
    socketio.emit('to_yh', data, broadcast=True)
    return "ok"
#---from iPhone iOS App

@app.route('/getorder', methods=['POST'])
def getorder():
    csn = request.json['csn']
    output = []
    appGetAllOrder(csn,0,output)
    appGetAllOrder(csn,1,output)
    return jsonify(output)
@app.route('/getfood', methods=['POST'])
def getfood():
    input_type = request.json['Type']
    output = []
    with conn.cursor() as cursor:
        sql = 'select * from food_list where Type = %s'
        cursor.execute(sql, input_type)
        results = cursor.fetchall()
        for i in results:
            a = {}
            a['FoodId'] = i[0]
            a['FoodName'] = i[4]
            a['FoodPrice'] = i[2]
            p = "static/img/food_picture/美味蟹堡.jpg"
            if os.path.exists("static/img/food_picture/{}.jpg".format(a['FoodName'])):
                p = "static/img/food_picture/{}.jpg".format(a['FoodName'])
            a['FoodPicStr'] = PathGetImageStr(p)
            output.append(a)
    return jsonify(output)
@app.route('/SendOrder',methods=['POST'])
def SendOrder():
    dnow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    res = {'result':'ok','order_time':dnow}
    content = request.json
    csn = content['CSN']
    val = []
    for i in content['order_list']:
        val.append((csn, dnow, i['number'], i['foodid']))
    with conn.cursor() as cursor:
        sql = "insert into Order_list (CN,Time,Number,Fid) values (%s,%s,%s,%s)"
        cursor.executemany(sql, val)
        conn.commit()
        socketio.emit('addOrder', "", broadcast=True)
    return jsonify(res)
@app.route('/LoginCustomer',methods=['POST'])
def LoginCustomer():
    res = {'result':'no'}
    content = request.json

    with conn.cursor() as cursor:
        username = content['Acc']
        password = content['Psw']
        sql = 'select * from Customer Where Acc = %s and Psw = %s'
        val = (username, password)
        cursor.execute(sql, val)
        results = cursor.fetchall()
        conn.commit()
        if results != ():
            res['result'] = 'ok'
            res['CSN'] = results[0][0]
            res['Sex'] = results[0][3]
            res['Name'] = results[0][4]
            res['Phone'] = results[0][5]
            res['Address'] = results[0][6]
            res['Birthday'] = results[0][7].strftime('%Y/%m/%d')
            res['Coin'] = results[0][9]
            res['Base64Img'] = 'no'
            img_path = "static/img/CustomerPic/{}.png".format(results[0][0])
            if not os.path.exists(img_path):
                img_path = "static/img/CustomerPic/user.png"
            with open(img_path, "rb") as imageFile:
                img_str = base64.b64encode(imageFile.read())
                res['Base64Img'] = img_str.decode('utf-8')
    print('LoginCustoer', content['Acc'],res['result'])
    return jsonify(res)
@socketio.on('connect')
def handle_connect():
    #print('Client connected',request.sid)
    clients.append(request.sid)
@socketio.on('disconnect')
def handle_disconnect():
    #print('Client disconnected')
    clients.remove(request.sid)
    #print(clients)

if __name__ == '__main__':
    socketio.run(app, host="192.168.1.6",port=40005,debug=True)
