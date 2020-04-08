import os
from flask import Flask, request, session
from flask_mysqldb import MySQL
from datetime import datetime
from flask import render_template
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from EncryptedModel import grocery_predict

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sahana'
app.config['MYSQL_DB'] = 'cn_self_study'
app.config['UPLOAD_FOLDER'] = './static/uploads'

mysql = MySQL(app)

@app.route("/")
@app.route("/index/")
def index():
    session['email']='63sahana@gmail.com'
    return render_template('indo.html')


@app.route("/choices/")
def choices():
    cur = mysql.connection.cursor()
    result = cur.execute("select details,image_html,type,modelid from model;")
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

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def writeTofile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")

def write_file(data, filename):
    with open("./static/results/" + filename, 'wb') as f:
        f.write(data[0].get('new_image'))

def read_file(data):
    with open("./static/results/temp.png", 'wb') as f:
        f.write(data)
    with open("./static/results/temp.png", 'r') as f:
        data=f.read()
    return data


@app.route("/uploadimage/",methods=['POST','GET'])
def imgup():
    if request.method == 'POST':
        title = request.form['title']
        file = request.files["filename"]
        print(title,file.filename)
        if file.filename == '':
            return render_template('ImgUp.html',error='no file uploaded')
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in set(['png', 'jpg', 'jpeg', 'gif']):
            try:
                print('saving file')
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print("Inserting BLOB into img table")
                cur = mysql.connection.cursor()
                old_image = convertToBinaryData("./static/uploads/" + filename)
                cur.execute(""" insert into user_data(email,data_uploaded)  VALUES (%s,%s);""",
                            (session['email'], old_image))
                # DL
                label=grocery_predict(filename)
                # add to database
                cur.execute("insert into prediction(modelid,label,dataid) values (%s,%s,%s);", (1,label,cur.lastrowid))
                mysql.connection.commit()
                cur.close()
                image_name = "../static/uploads/" + filename
                return render_template("predict.html", image_name=image_name,label=label,title=title)
            except:
                error = 'could predict label'
                return render_template('ImgUp.html', error=error)
        else:
            error = 'File not an image'
            return render_template('ImgUp.html', error=error)

    return render_template("ImgUp.html")

@app.route("/uploadsound/")
def soundup():
    return render_template("SoundUp.html")

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug = True)
