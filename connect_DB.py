from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import Flask,render_template, request, flash, session, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, not_
from utils import * 
import re
from io import BytesIO
import base64
import sqlalchemy.orm

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
    
    if request.method == 'GET':
        # Decode image from database
        if shop_info:
            item_all = db.session.query(item_).filter(item_.SID == shop_info[0].SID).all()
            for i in range(len(item_all)):
                image = base64.b64encode(item_all[i].content).decode()
                item_all[i].content = image
            return render_template("nav.html", shop_info = shop_info, item_all = item_all)
        else:
            return render_template("nav.html")

    elif request.method == 'POST':
        # Add items
        if request.form['hidden'] == "add_item":
            item_info = request.form
            img = request.files['myFile']

            newitem = item_(None, 
                            shop_info[0].SID,  
                            item_info["meal_name"],
                            item_info["price"], 
                            img.read(),
                            item_info["amount"])
                                
            keys = ['meal_name', 'price', 'amount']
            empty_message = {
                'meal_name': 'Meal name can\'t be empty.',
                'price': 'Price can\'t be empty.',
                'amount': 'Quantity can\'t be empty.',
                'myFile': 'You should at least upload an image.',
            }

            error_message = {
                'meal_name': "",
                'price': 'Your price must contain only non-negative numbers.',
                'amount': 'Your quantity must contain only non-negative numbers.',
            }

            Patterns = {
                'meal_name': lambda s: len(s)!=0,
                'price': lambda s : (re.match('^\d+$', s) != None) and (int(s)>=0),
                'amount': lambda s : (re.match('^\d+$', s) != None) and (int(s)>=0),
            }

            ret = {'success': True}

            for key in keys :
                ret.update({key: ''})

            # Check type
            for key in keys:
                if not Patterns[key](item_info[key]) :
                    ret.update({key: error_message[key]})
                    ret.update({'success': False})
            
            # Check empty
            for key in keys:
                if key not in item_info.keys() or len(item_info[key]) == 0:
                    ret.update({key: empty_message[key]})
                    ret.update({'success': False})
            if not img:
                ret.update({'myFile': empty_message["myFile"]})
                ret.update({'success': False})


            if ret["success"]:
                db.session.add(newitem)
                db.session.commit()


            return jsonify(ret)

        # Edit items
        elif request.form['hidden'] == "edit_item":
            edit_item = request.form
            pick_item = db.session.query(item_).filter(
                                item_.SID == shop_info[0].SID,
                                item_.item_name == edit_item['item_name']
                                
                        ).first()
            pick_item.price = request.form['new_price']
            pick_item.amount = request.form['new_quantity']

            keys = ['new_price', 'new_quantity']
            empty_message = {
                'new_price': 'Price can\'t be empty.',
                'new_quantity': 'Quantity can\'t be empty.',
            }

            error_message = {
                'new_price': 'Your price must contain only non-negative numbers.',
                'new_quantity': 'Your quantity must contain only non-negative numbers.',
            }

            Patterns = {
                'new_price': lambda s : (re.match('^\d+$', s) != None) and (int(s)>=0),
                'new_quantity': lambda s : (re.match('^\d+$', s) != None) and (int(s)>=0),
            }

            ret = {'success': True}

            for key in keys :
                ret.update({key: ''})

            # Check type
            for key in keys:
                if not Patterns[key](edit_item[key]) :
                    ret.update({key: error_message[key]})
                    ret.update({'success': False})

            # Check empty
            for key in keys:
                if key not in edit_item.keys() or len(edit_item[key]) == 0:
                    ret.update({key: empty_message[key]})
                    ret.update({'success': False})

            if ret["success"]:
                db.session.commit()
            
            return jsonify(ret)

        # Delete items
        elif request.form['hidden'] == "delete_item":
            delete_item = request.form
            db.session.query(item_).filter(
                                item_.SID == shop_info[0].SID,
                                item_.item_name == delete_item['item_name']
                                
                        ).delete()
                
            db.session.commit()

            ret = {'success': True}

            return jsonify(ret)
        
        # # Update item image
        # item_all = db.session.query(item_).filter(item_.SID == shop_info[0].SID).all()
        # for i in range(len(item_all)):
        #     image = base64.b64encode(item_all[i].content).decode()
        #     item_all[i].content = image

        # return render_template("nav.html", shop_info = shop_info, item_all = item_all)


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