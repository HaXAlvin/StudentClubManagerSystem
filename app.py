from flask import Flask, render_template, request, jsonify
import pymysql
import pandas
from bs4 import BeautifulSoup
app = Flask(__name__)
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='qwer25604677',  # getpass('pass')
    db='iosclub',
    charset='utf8mb4',
)


@app.route('/')  # address
def hello_world():
    return render_template('index.html')


@app.route('/searchName', methods=['POST'])  # API
def search_name():
    res = {'result': 'no'}
    try:
        with conn.cursor() as cursor:
            name = request.form['name']
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
    except Exception as error_message:
        conn.ping(True)  # true = reconnect
        res['result'] = error_message
    return jsonify(res)  # 回傳json格式
# if results:
#   res['result'] = 'yes'
#   res['member_id'] = results[0][0]
#   res['member_name'] = results[0][1]
#   res['member_nid'] = results[0][2]
#   res['submission_date'] = results[0][3]


@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動
