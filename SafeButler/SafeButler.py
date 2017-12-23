import json
import os
import sqlite3
import time
import collections
from flask import render_template, request
from flask import Flask

app = Flask(__name__)

dict = {}
dict["tom@safebutler.com"] = "tom"


@app.route('/')
def login_page():
    connection = sqlite3.connect('addresses.db')
    cursor_reference = connection.cursor()
    cursor_reference.execute('''DROP TABLE IF EXISTS ADDRESSES''')
    cursor_reference.execute('''CREATE TABLE ADDRESSES(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                DATE_INFO TEXT,
                                PRICE INTEGER,
                                QUOTE_TIME INTEGER)''')
    connection.commit()
    connection.close()
    return render_template('index.html')


@app.route('/login_credentials', methods=['POST', 'GET'])
def login():
    uname = request.args.get('username')
    password = request.args.get('password')
    # print(uname,password)
    if uname in dict and dict[uname] == password:
        filename = os.path.join(app.static_folder, 'json_data')
        with open(filename) as blog_file:
            info = json.load(blog_file)
        # print(info,len(info))
        length_of_message = len(info)
        if len(info) >= 0:
            return render_template('agent.html', username=uname, data=info, len=length_of_message)
    return render_template('index.html', error="Wrong UserName/Password")


@app.route('/showclients', methods=['POST', 'GET'])
def clients():
    filename = os.path.join(app.static_folder, 'json_data')
    with open(filename) as file:
        info = json.load(file)
    return render_template('showclients.html', data=info)


@app.route('/insertdb', methods=['POST', 'GET'])
def boom():
    quote_time = int(time.time() * 1000) - int(request.args.get('start_key'))
    connection = sqlite3.connect('addresses.db')
    cursor_reference = connection.cursor()
    date_info = str(sqlite3.datetime.datetime.now().month) + "/" + str(sqlite3.datetime.datetime.now().year)
    cursor_reference.execute(
        '''INSERT INTO ADDRESSES(DATE_INFO,PRICE,QUOTE_TIME)VALUES (?,?,?)''',
        (date_info, str(request.args.get('Price')),
         quote_time))
    """
    Force Entry into database
    date_inf = str(sqlite3.datetime.datetime.now().month) + "/" + str(sqlite3.datetime.datetime.now().year + 1)
    cursor_reference.execute(
        '''INSERT INTO ADDRESSES(DATE_INFO,PRICE,QUOTE_TIME)VALUES (?,?,?)''',
        (date_inf, str(0),
         quote_time))
    """
    connection.commit()
    connection.close()
    return "Quote is sent"


@app.route('/agent_perfomance', methods=['POST', 'GET'])
def agent():
    connection = sqlite3.connect('addresses.db')
    cursor_reference = connection.cursor()
    cursor_reference.execute('''SELECT DISTINCT DATE_INFO FROM ADDRESSES''')
    query_date = cursor_reference.fetchall()
    final_output = collections.OrderedDict()
    for q in query_date:
        month_year = str(q[0])
        cursor_reference.execute('''SELECT COUNT(*) FROM ADDRESSES WHERE DATE_INFO=?''', (month_year,))
        quotes_finished = int(cursor_reference.fetchall()[0][0])
        cursor_reference.execute('''SELECT AVG(PRICE) FROM ADDRESSES WHERE DATE_INFO=?''', (month_year,))
        average_price = int(cursor_reference.fetchall()[0][0])
        cursor_reference.execute('''SELECT MAX(PRICE) FROM ADDRESSES WHERE DATE_INFO=?''', (month_year,))
        max_price = int(cursor_reference.fetchall()[0][0])
        cursor_reference.execute('''SELECT MIN(PRICE) FROM ADDRESSES WHERE DATE_INFO=?''', (month_year,))
        min_price = int(cursor_reference.fetchall()[0][0])
        cursor_reference.execute('''SELECT AVG(QUOTE_TIME) FROM ADDRESSES WHERE DATE_INFO=?''', (month_year,))
        quote_time = int(cursor_reference.fetchall()[0][0])
        m_y = collections.OrderedDict()
        m_y["quotes_finished"] = quotes_finished
        price = collections.OrderedDict()
        price["average"] = average_price
        price["max_price"] = max_price
        price["min_price"] = min_price
        m_y["price"] = price
        value = collections.OrderedDict()
        value["average"] = quote_time
        m_y["quote_time"] = value
        final_output[month_year] = m_y
    json_string = json.dumps(final_output, sort_keys=True, indent=4, separators=(',', ': '))
    connection.commit()
    connection.close()
    return json_string


if __name__ == '__main__':
    app.run()
