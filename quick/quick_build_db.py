from time import sleep
import pandas
import pymysql
from hashlib import sha512


def executeScriptsFromFile(filename):
    with open(filename, 'r') as fd:
        sql_file = fd.read()
    sql_commands = sql_file.split(';')
    for command in sql_commands:
        if command == '':
            continue
        try:
            cursor.execute(command)
        except Exception as error_message:
            print("Command skipped: ", error_message)


def dropTable(tableName):
    try:
        cursor.execute(f'drop table if exists {tableName};')
    except Exception as error_message:
        print("Command skipped: ", error_message)


conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='qwer25604677',
    db='iosclub',
    charset='utf8mb4',
)
cursor = conn.cursor()

dropTable("class_state")
dropTable("rtc_state")
dropTable("memberlist")
dropTable("comment")
dropTable("announcement")

executeScriptsFromFile('create_table.sql')

df = pandas.read_csv("member_list.csv").T
for i in range(df.shape[1]):
    seed = df[i][2] if df[i][9] == 'None' else df[i][9]
    pwd = sha512(seed.encode('utf-8')).hexdigest().upper()
    manager = df[i][10]
    val = (df[i][0], df[i][1], df[i][2], df[i][3], df[i][4], df[i][5], df[i][6], df[i][7], df[i][8], pwd, manager)
    print(val)
    sql = "insert into memberlist VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    cursor.execute(sql, val)
conn.commit()

df = pandas.read_csv("punch_in.csv")
print(df)
sql = 'insert into class_state (member_id,date,attendance,register) values (%s,%s,%s,%s);'
for i in range(1, len(df.columns)):
    time = df.columns[i][:10].split('.')
    for line in df.values:
        Bool = str(line[i]).upper()
        att = 1 if Bool == 'TRUE' else 0
        rei = 0 if Bool == 'FALSE' else 1
        val = (line[0], f'{time[0]}-{time[1]}-{time[2]} 00:00:00', att, rei)
        print(val)
        try:
            cursor.execute(sql, val)
        except Exception as msg:
            print("Command skipped: ", msg)
conn.commit()

df = pandas.read_csv("announcement.csv").T
for i in range(df.shape[1]):
    val = (df[i][0], df[i][1], df[i][2], df[i][3], df[i][4], df[i][5])
    print(val)
    sql = "insert into announcement VALUE (%s,%s,%s,%s,%s,%s);"
    cursor.execute(sql, val)
conn.commit()


