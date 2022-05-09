from flask import Flask,render_template, request, flash, session, redirect, url_for
from flask_mysqldb import MySQL
 
app = Flask(__name__)
app.secret_key = "2222222"
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'food_platform'

mysql = MySQL(app)

#Creating a connection cursor
if mysql:
   print("Connection Successful!")
else:
   print("Connection Failed!") 

 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
     
    elif request.method == 'POST':
        print(request.form)
        acc = request.form['Account']
        pw = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT account, password from user")
        data = cursor.fetchall()
        mysql.connection.commit()
        for (account, password) in data:
            if acc == account and pw == password:
                return redirect(url_for('nav'))
        cursor.close()
        flash("登入失敗")
        return redirect(url_for('login'))
    
@app.route('/nav', methods = ['GET', 'POST'])
def nav():
    return render_template("nav.html")

@app.route('/sign-up', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("sign-up.html")
    
    elif request.method == 'POST':
        acc = request.form['_Account']
        name = request.form['_name']
        password = request.form['_password']
        re_pass = request.form['_re-password']
        phone_num = request.form['_phonenumber']
        latitude = request.form['_latitude']
        longitude = request.form['_longitude']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT account from user")
        mysql.connection.commit()
        prev_accs = cursor.fetchall()
        
        if not name or not acc or not password or not re_pass or not phone_num or not latitude or not longitude:
            flash("欄位空白！")
            cursor.close()
            return redirect(url_for('signup'))

        elif (acc,) in prev_accs:
            flash("帳號已被註冊！")
            cursor.close()
            return redirect(url_for('signup'))

        elif len(phone_num) > 10 or not phone_num.isdigit():
            flash("電話號碼格式錯誤(限10位以內數字)")
            cursor.close()
            return redirect(url_for('signup'))

        elif not acc.isalpha():
            flash("帳號格式錯誤(限大小寫英文)")
            cursor.close()
            return redirect(url_for('signup'))

        elif not password.isalpha():
            flash("密碼格式錯誤(限大小寫英文)")
            cursor.close()
            return redirect(url_for('signup'))

        elif not latitude.isdigit() or not longitude.isdigit():
            flash("經緯度格式錯誤(限數字)")
            cursor.close()
            return redirect(url_for('signup'))
        
        elif password!=re_pass:
            flash("密碼驗證不等於密碼！")
            cursor.close()
            return redirect(url_for('signup'))
        
        cursor.execute("INSERT INTO user (account, name, password, phone, lat, lng) VALUES (%s, %s, %s, %s, %s, %s)", (acc, name, password, int(phone_num), int(latitude), int(longitude)))
        mysql.connection.commit()
        flash("登入成功")
        cursor.close()
        print("hleee")
        
        return redirect(url_for('login'))
        
app.run(host='localhost', port=5000)