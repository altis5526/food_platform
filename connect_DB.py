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
     
    if request.method == 'POST':
        acc = request.form['Account']
        pw = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * from login")
        data = cursor.fetchall()
        mysql.connection.commit()
        for (account, password) in data:
            print(account, password)
            if acc == account and pw == password:
                print(acc, pw)
                print(account, password)
                print("good")
                return redirect(url_for('nav'))
        cursor.close()
        flash("登入失敗")
        return redirect(url_for('login'))
    
@app.route('/nav', methods = ['GET', 'POST'])
def nav():
    return render_template("nav.html")

@app.route('/sign-up', methods = ['GET', 'POST'])
def signup():
    return render_template("sign-up.html")

 
app.run(host='localhost', port=5000)