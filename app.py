from flask import Flask
from flask_mysqldb import MySQL
from datetime import datetime
from flask import render_template
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sahana'
app.config['MYSQL_DB'] = 'cn_self_study'

mysql = MySQL(app)

@app.route("/")
@app.route("/index/")
def index():
    return render_template('indo.html')

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        'hello_there.html',
        name=name,
        date=datetime.now()
    )

@app.route("/choices/")
def choices():
    cur = mysql.connection.cursor()
    result = cur.execute("select details,image_html,type from model;")
    models = cur.fetchall()
    link_list=[]
    for i in models:
        if i[2]=='NLP':
            link_list.append('/uploadtext/')
        elif i[2]=='CNN':
            link_list.append('/uploadimage/')
        elif i[2]=='Sound':
            link_list.append('/uploadsound/')
    if result > 0:
        return render_template('choices.html', models=models,link_list=link_list,len=len(link_list))
    cur.close()
    return render_template("choices.html")

@app.route("/uploadtext/")
def textup():
    return render_template("TextUp.html")

@app.route("/uploadimage/")
def imgup():
    return render_template("ImgUp.html")

@app.route("/uploadsound/")
def soundup():
    return render_template("SoundUp.html")

app.run(debug=True)