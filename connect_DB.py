from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import Flask,render_template, request, flash, session, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, not_
from utils import * 
import re
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "2222222"
 
# MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root@localhost:3306/food_platform"

db = SQLAlchemy(app)

# init login manager
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass

# def read_image(filename):
#     #Convert digital data to binary format
#     with open(filename, 'rb') as f:
#         photo = f.read()
#         photo = photo.decode("utf-16")
#     return photo

@login_manager.user_loader  
def user_loader(ID):

    data = db.session.query(user_).filter(user_.UID == ID).first()
    if data == None:
        return
    user = User()
    user.id = ID
    return user


## --------------------------------------- Web ------------------------------------------ ##

@app.route('/')
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
     
    if request.method == 'POST':
        
        acc = request.form['Account']
        pw = request.form['password']
        
        # query db
        data = db.session.query(user_).filter(user_.account == acc).first()
        
        if data != None and data.password == pw:
            # login 
            user = User()
            user.id = data.UID 
            login_user(user) 
            return redirect(url_for('nav'))
        
        flash("登入失敗")
        return redirect(url_for('login'))
    
@app.route('/nav', methods = ['GET', 'POST'])
@login_required
def nav():
    curr_userID = current_user.get_id()
    shop_info = db.session.query(shop_).filter(shop_.UID == curr_userID).all()
    item_all = db.session.query(item_).filter(item_.SID == shop_info[0].SID).all()
    
    if request.method == 'GET':
        # Decode image from database
        print(len(item_all))
        for i in range(len(item_all)):
            image = base64.b64encode(item_all[i].content).decode()
            item_all[i].content = image
        return render_template("nav.html", shop_info = shop_info, item_all = item_all)

    elif request.method == 'POST':
        # Add items
        if request.form['hidden'] == "add_item":
            item_info = request.form
            img = request.files['myFile']
            print(request.form)

            newitem = item_(None, 
                            shop_info[0].SID,  
                            item_info["meal_name"],
                            item_info["price"], 
                            img.read(),
                            item_info["amount"])
                                
            db.session.add(newitem)
            db.session.commit()

        # Edit items
        elif request.form['hidden'] == "edit_item":
            edit_item = request.form
            pick_item = db.session.query(item_).filter(
                                item_.SID == shop_info[0].SID,
                                item_.item_name == edit_item['item_name']
                                
                        ).first()
            pick_item.price = request.form['new_price']
            pick_item.amount = request.form['new_quantity']
        
            db.session.commit()

        elif request.form['hidden'] == "delete_item":
            delete_item = request.form
            pick_item = db.session.query(item_).filter(
                                item_.SID == shop_info[0].SID,
                                item_.item_name == delete_item['which_item']
                                
                        ).first()
            print(pick_item)
            if pick_item:
                print("hello")
                db.session.delete(pick_item)
                db.session.commit()

        return render_template("nav.html", shop_info = shop_info, item_all = item_all)

# @app.route('/images/0.jpg')
# def get_image():
#     curr_userID = current_user.get_id()
#     item_all = db.session.query(item_).filter(shop_.UID == curr_userID).all()
#     download_img = send_file(BytesIO(download_img), mimetype='image/png', as_attachment=True, attachment_filename=True)
#     return download_img

@app.route('/sign-up', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("sign-up.html")

    if request.method == 'POST':
        message = request.form
        keys = ['name', 'phonenumber', 'Account', 'password', 're-password', 'latitude', 'longitude']
        empty_message = {
            'name': 'Name can\'t be empty.',
            'phonenumber': 'Please fill in your phone number.',
            'Account': 'Account can\'t be empty.',
            'password': 'Please fill in your password.',
            're-password': 'Please repeat your password.',
            'latitude': 'latitude can\'t be empty', 
            'longitude': 'longitude can\'t be empty'
        }
        error_message = {
            'name': 'Your name must contain only latin letters.',
            'phonenumber': 'Your phone number must be a 10-digit number.',
            'Account': 'Your account must contain only latin letters and numbers.',
            'latitude': 'Latitude must be a number between -90 and 90.', 
            'longitude': 'Longitude must be a number between -180 and 180.'
        }
        Patterns = {
            'name': lambda s : re.match('^[A-Za-z]+$', s) != None,
            'phonenumber': lambda s : re.match('^\d{10}$', s) != None,
            'Account': lambda s : re.match('^[a-zA-Z0-9]+$', s) != None,
            'latitude': lambda s : isFloat(s) and -90 <= float(s) and 90 >= float(s),
            'longitude': lambda s : isFloat(s) and -180 <= float(s) and 180 >= float(s)
        }
        ret = {'success': True}
        
        for key in keys :
            ret.update({key: ''})

        # Check empty
        for key in keys:
            if key not in message.keys() or len(message[key]) == 0:
                ret.update({key: empty_message[key]})
                ret.update({'success': False})

        # Check value
        for key in Patterns.keys() :
            if not Patterns[key](message[key]) :
                ret.update({key: error_message[key]})
                ret.update({'success': False})

        # Check repeat 
        if message['password'] != message['re-password'] :
            ret.update({'re-password': 'Re-password is different from password.'})
            ret.update({'success': False})

        # Check account exists
        data = db.session.query(user_).filter(user_.account == message['name']).first()

        if data != None :
            ret.update({'name': 'The account already exists.'})
            ret.update({'success': False})
            

        if ret['success'] :
            
            newuser = user_(None, 
                         message['Account'],
                         message['name'], 
                         message['password'],
                         message['phonenumber'],
                         message['latitude'],
                         message['longitude'])
                             
            db.session.add(newuser)
            db.session.commit()
            

        return jsonify(ret)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
    
app.run(host = 'localhost', port = 5000, debug = True)