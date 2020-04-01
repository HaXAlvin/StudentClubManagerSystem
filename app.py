from flask import Flask, render_template, request
import pymysql
app = Flask(__name__)
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='0000',
    db='iosclub',
    charset='utf8mb4',
)


@app.route('/')  # address
def hello_world(name=None):
    return render_template('index.html', name=name)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html', results=None)
    elif request.method == 'POST':
        with conn.cursor() as cursor:
            name = request.form['name']
            sql = "SELECT * FROM memberList WHERE member_name =%s;"
            cursor.execute(sql, name)
            results = cursor.fetchall()[0]
            return render_template('search.html', results=results)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5277, debug=True)  # debug = true 隨時變動
