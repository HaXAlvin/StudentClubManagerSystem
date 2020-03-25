from flask import Flask, render_template
import pymysql
app = Flask(__name__)
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='0000',
    db='iosclub',
    charset='utf8mb4',
)
with conn.cursor() as cursor:
    sql = 'SELECT * FROM memberList;'
    cursor.execute(sql)
    results = cursor.fetchall()
    for i in results:
        print(i)


@app.route('/')  # address
def hello_world():
    return render_template('index.html', name='alvin')


@app.route('/<name>', methods=['GET', 'POST'])
def detail(name=None):
    with conn.cursor() as cursor:
        sql = "SELECT * FROM memberList WHERE member_name =%s;"
        cursor.execute(sql, name)
        results = cursor.fetchall()
        return str(results)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動
