from flask import Flask, request, render_template, send_from_directory, abort, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import requests
import os
from werkzeug.utils import redirect
from random import randint
from time import time
import json

configs = json.load(open('config.json'))

app = Flask(__name__)
app.config['MYSQL_HOST'] = str(configs['mysql-db']['host'])
app.config['MYSQL_USER'] = str(configs['mysql-db']['user'])
app.config['MYSQL_PASSWORD'] = str(configs['mysql-db']['password'])
app.config['MYSQL_DB'] = str(configs['mysql-db']['database'])
mysql = MySQL(app)
app.secret_key = 'sdgkdncnipewivb24968956dlvkn'
somestr = '102952697000msherfa123001210934785627346'
someotherstr = str(randint(-1000000000, 1000000001)) + str(time()*100000000) + str(randint(-1000000000, 1000000001))
noimgs = len(os.listdir(os.path.join('./', 'ad3ya')))

latitude, longitude = open('config/coordinates.txt').read().split(',')

def get_pt():
    pt = []
    d = datetime.today()
    r = requests.get("https://api.aladhan.com/v1/calendar?latitude={}&longitude={}&method=4&month={}&year={}".format(latitude, longitude, d.month, d.year))
    r = r.json()['data'][d.day-1]['timings']
    pt.append("الفجر: " + r['Fajr'].split(' ')[0])
    pt.append("الظهر: " + r['Dhuhr'].split(' ')[0])
    pt.append("العصر: " + r['Asr'].split(' ')[0])
    pt.append("المغرب: " + r['Maghrib'].split(' ')[0])
    pt.append( "العشاء: " + r['Isha'].split(' ')[0])
    print(r)
    return pt

class statics():
    pt = get_pt()
    currentday = datetime.today().day
    trys = {}
    
    def changecurrentday(self):
        if(datetime.today().day != self.currentday):
            self.currentday = datetime.today().day
            self.pt = get_pt()
            self.trys = {}

static = statics()

def getdata():
    static.changecurrentday()
    data = []
    cur = mysql.connection.cursor()
    d1 = datetime.today() - timedelta(days=2)
    d2 = datetime.today() + timedelta(days=7)
    sql = f"SELECT * FROM {configs['mysql-db']['table']} WHERE ddate BETWEEN '{d1.year}-{d1.month}-{d1.day}' AND '{d2.year}-{d2.month}-{d2.day}' ORDER BY ddate ASC"
    cur.execute(sql)
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return data

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', data=getdata(), pt=static.pt, sometimevar=time())

@app.route('/a', methods=['POST', 'GET'])
def adde():
    if 'v' not in session:
        return redirect("/l")
    if session.get('v') != someotherstr:
        return redirect("/l")
    if request.method == 'POST':
        data = request.form
        print(data)
        cur = mysql.connection.cursor()
        sql = f"INSERT INTO {configs['mysql-db']['table']} (ddate, day, name, event, time) VALUES ('{data['ddate']}', '{data['day']}', '{data['name']}', '{data['event']}', '{data['time']}');"
        cur.execute(sql)
        mysql.connection.commit()
        cur.close()
    return render_template('adde.html', data=getdata(), pt=static.pt)

@app.route('/dele', methods=['GET', 'POST'])
def dele():
    if request.method == 'GET':
        abort(404)
    if 'v' not in session:
        return redirect("/l")
    if session.get('v') != someotherstr:
        return redirect("/l")
    hashtag = request.form
    print(hashtag, request.method, request.remote_addr)
    hashtag = hashtag['hashtag']
    if (not hashtag.isnumeric()) or int(hashtag) < -1:
        abort(404)
    cur = mysql.connection.cursor()
    sql = f"DELETE FROM {configs['mysql-db']['table']} WHERE id LIKE " + hashtag + ";"
    cur.execute(sql)
    mysql.connection.commit()
    cur.close()
    return redirect('/a')

@app.route("/l", methods=['POST', 'GET'])
def login():
    if request.remote_addr in static.trys and int(static.trys.get(str(request.remote_addr))) >= 5:
        abort(401)
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        data = request.form
        print(data)
        print(''.join([data['p' + str(i+1)] for i in range(5)]))
        if ''.join([data['p' + str(i+1)] for i in range(5)]) == '1'+'1'+somestr[12:22]+'1'+'1':
            session['v'] = someotherstr
            return redirect("/a")
        if request.remote_addr not in static.trys:
            static.trys[str(request.remote_addr)] = 1
        else:
            static.trys[str(request.remote_addr)] = int(static.trys.get(str(request.remote_addr))) + 1
        return render_template("login.html")

@app.route('/favicon.ico')
def favicon():
   return send_from_directory(os.path.join('./', 'static'), 'favicon.ico')

@app.route('/ad3ya')
def ad3ya():
    if 'imgno' not in session:
        session['imgno'] = 1
    if int(session.get('imgno')) >= noimgs:
        session['imgno'] = 1
    session['imgno'] += 1
    return send_from_directory(os.path.join('./', 'ad3ya'), str(session.get('imgno')) + '.jpg')

app.run(host=configs['server']['host'], port=configs['server']['port'], debug=configs['server']['debug'])
