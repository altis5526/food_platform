import json
from sre_constants import SUCCESS
from unicodedata import category
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask import Flask,render_template, request, flash, session, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from functools import wraps
import numpy as np
from utils import * 
import base64

app = Flask(__name__)
app.secret_key = "2222222"
 
# MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root@localhost:3306/food_platform"

db = SQLAlchemy(app)

# init login manager
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('_user_id') is None:
            return redirect(url_for('login', next = request.url))
        return func(*args, **kwargs)
    return decorated_function


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
def home():
    if session.get('_user_id') is None:
        return redirect(url_for('login'))
    else:
        return redirect('/nav?#home')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
     
    if request.method == 'POST':
        print(request.form)
        acc = request.form['account']
        pw = request.form['password']
        
        # query db
        data = db.session.query(user_).filter(user_.account == acc).first()
        
        if data != None and data.password == pw:
            # login 
            user = User()
            user.id = data.UID 
            login_user(user) 
            return jsonify({'success': True})
        
        return jsonify({'success': False})

@app.route('/update', methods = ['POST'])
@login_required
def update():
    message = request.form

    if message['type'] == 'password' :
        print('update user password: ', message)
        userID = session.get('_user_id')
        data = db.session.query(user_).filter(user_.UID == userID).first()

        if message['password'] != message['repassword'] :
            return jsonify({'success': False, 'message': 'The re-password is different from your password.'})

        data.password = message['password']
        db.session.commit()

        return jsonify({'success': True})
    
    if message['type'] == 'profile':
        print('update user profile: ', message)
        keys = ['name', 'phone', 'latitude', 'longitude']

        ret = checkEmptyAndValue(message, keys)
        
        if ret['success'] :
            
            userID = session.get('_user_id')
            data = db.session.query(user_).filter(user_.UID == userID).first()

            data.name = message['name']
            data.phone = message['phone']

            data.lat = message['latitude']
            data.lng = message['longitude']
            data.position = 'POINT({} {})'.format(message['latitude'], message['longitude'])
            print('success')

            db.session.commit()
            

        return jsonify(ret)

    if message['type'] == 'add':
        print('add user balance: ', message)
        if not isInteger(message['add']) :
            return jsonify({'success': False, 'message': 'Add value should be an integer.'})

        userID = session.get('_user_id')
        data = db.session.query(user_).filter(user_.UID == userID).first()

        data.balance = data.balance + int(message['add'])

        db.session.commit()

        return jsonify({'success': True, 'value': str(data.balance)})

    if message['type'] == 'addShop':
        print('add shop for user: ', message)
        keys = ['shop_name', 'food_category', 'latitude', 'longitude']        

        ret = checkEmptyAndValue(message, keys)

        # check duplicates
        if 'shop_name' in message.keys() and len(message['shop_name']) != 0:
            shopInfo = db.session.query(shop_).filter(shop_.shop_name == message['shop_name']).first()
            print(shopInfo)
            if (shopInfo != None):
                ret.update({'shop_name': 'This shop name is already registered!!'})
                ret.update({'success': False})

        if ret['success']:
            user_id = session.get('_user_id')

            newshop = shop_(None, 
                         user_id,
                         message['shop_name'], 
                         message['latitude'],
                         message['longitude'],
                         '0979797979',
                         message['food_category'])
            
            db.session.add(newshop)
            db.session.commit()


        return jsonify(ret)

    if message['type'] == 'updShop':
        print('update shop for user: ', message)
        keys = ['shop_name', 'food_category', 'latitude', 'longitude']        

        ret = checkEmptyAndValue(message, keys)

        userID = session.get('_user_id')

        # check duplicate
        if 'shop_name' in message.keys() and len(message['shop_name']) != 0:
            shopInfo = db.session.query(shop_).filter(shop_.shop_name == message['shop_name']).first()
            print(shopInfo)
            if (shopInfo != None) and int(shopInfo.UID) != int(userID):
                print(shopInfo.UID, userID)
                ret.update({'shop_name': 'This shop name is already registered!!'})
                ret.update({'success': False})

        if ret['success'] :
            
            yourShop = db.session.query(shop_).filter(shop_.UID == userID).first()
            
            yourShop.shop_name = message['shop_name']
            yourShop.type = message['food_category']
            yourShop.lat = message['latitude']
            yourShop.lng = message['longitude']
            yourShop.position = 'POINT({} {})'.format(message['latitude'], message['longitude'])

            db.session.commit()

        print(ret)    

        return jsonify(ret)
    
    if message['type'] == 'add_item':
        print('Add item : ', message)
        keys = ['meal_name', 'price', 'amount']
        
        image = None if 'myFile' not in request.files.keys() else request.files['myFile']

        ret = checkEmptyAndValue(message, keys)
        
        if not image:
            ret.update({'myFile': empty_message['myFile']})
            ret.update({'success': False})
        
        if ret['success']:

            userID = session.get('_user_id')
            yourShop = db.session.query(shop_).filter(shop_.UID == userID).first()
            

            newItem = item_(None, 
                            yourShop.SID,
                            message['meal_name'],
                            message['price'],
                            image.read(),
                            message['amount'])

            db.session.add(newItem)
            db.session.commit()
        
        return jsonify(ret)

    if message['type'] == 'editItem':
        print('Edit item : ', message)
        keys = ['price', 'amount']

        PID = int(message['PID'])
        yourItem = db.session.query(item_).filter(item_.PID == PID).first()
        if yourItem:
            tmp = checkEmptyAndValue(message, keys)
            if tmp['success']:
                yourItem.amount = message['amount']
                yourItem.price = message['price']
                db.session.commit()
                return jsonify({'success': True})
            else:
                ret = {'success': False}
                ret.update({'new_price': tmp['price']})
                ret.update({'new_quantity': tmp['amount']})

            return jsonify(ret)
        else:
            # No such item (This should not happen...)
            return jsonify({'success': False})

    if message['type'] == 'delete_item':
        PID = int(message['PID'])
        itemInfo = db.session.query(item_).filter(item_.PID == PID).first()
        if itemInfo:
            db.session.delete(itemInfo)
            db.session.commit()
            return jsonify({'success': True})
        else :
            return jsonify({'success': False})

    if message['type'] == 'order':
        print('User send order: ', message)
        PIDS = message['order'].split(',')
        
        for PID in PIDS :
            if isInteger(PID) :
                pass # Not implemented yet...
        return jsonify({'success': True})
        

@app.route('/ask', methods = ['POST'])
@login_required
def ask():
    message = request.form
    if message['type'] == 'findShop' :
        print('Searching for: ', message)

        shopNames = message['shopName'].split()
        categorys = message['category'].split() # shop type
        distanceType = {"near": 1000, "medium": 10000, "far": 1000000} # Distance type
        distance = 1000000000000000 if message['distance'] not in distanceType.keys() else distanceType[message['distance']]
    
        meals = message['meal'].split()
        lowerPrice = None if not isInteger(message['lowerPrice']) else int(message['lowerPrice'])
        upperPrice = None if not isInteger(message['upperPrice']) else int(message['upperPrice'])
        
        filter_item = False
        if len(meals) > 0 or lowerPrice is not None or upperPrice is not None :
            filter_item = True

        userID = session.get('_user_id')
        userPos = str(db.session.query(user_.position).filter(user_.UID == userID).first()[0])

        if filter_item:

            # select with constrain on shop
            
            rule1 = and_(
                *[func.UPPER(shop_.shop_name).like(func.UPPER('%' + shopName + '%')) for shopName in shopNames], 
                *[func.UPPER(shop_.type).like(func.UPPER('%' + cat + '%')) for cat in categorys], 
                True if distance is None else  func.ST_Distance_Sphere(func.ST_GeomFromText(shop_.position), func.ST_GeomFromText(userPos)) < distance
            )
            # First select SID with filter on distance, type, and shopName
            shops1 = db.session.query(shop_.SID).filter(rule1).all() 

            
            # select with constrain on item
            
            SIDS = []
            for shop in shops1 :
                SIDS.append(shop[0])
            rule2 = and_(
                item_.SID.in_(SIDS),
                *[func.UPPER(item_.item_name).like(func.UPPER('%' + item_name + '%')) for item_name in meals] ,
                True if lowerPrice is None else item_.price >= lowerPrice,
                True if upperPrice is None else item_.price <= upperPrice,
            )
            
            shops2 = db.session.query(item_.SID).distinct().filter(rule2).all()
            SIDS = []
            for shop in shops2 :
                SIDS.append(shop[0])
            result = db.session.query(shop_, func.ST_Distance_Sphere(func.ST_GeomFromText(shop_.position), func.ST_GeomFromText(userPos))).filter(shop_.SID.in_(SIDS)).all()
            """
            with shop2 as (
                with shop1 as (
                    select SID from shop where rule1_is_matched
                )
                select SID
                from shop
                where SID in shop1.SID and rule2_is_matched
            )
            select * from shop where SID in result
            """
        else :

            rule1 = and_(
                *[func.UPPER(shop_.shop_name).like(func.UPPER('%' + shopName + '%')) for shopName in shopNames], 
                *[func.UPPER(shop_.type).like(func.UPPER('%' + cat + '%')) for cat in categorys], 
                True if distance is None else  func.ST_Distance_Sphere(func.ST_GeomFromText(shop_.position), func.ST_GeomFromText(userPos)) < distance
            )
            result = db.session.query(shop_, func.ST_Distance_Sphere(func.ST_GeomFromText(shop_.position), func.ST_GeomFromText(userPos))).filter(rule1).all() 

            """
            with shop1 as (
                select SID from shop where rule1_is_matched
            )
            select * from shop where SID in shop1.SID
            """
        def getDis(d):
            label = ['near', 'medium']
            value = [30000, 150000]    
            for i in range(len(label)) :
                if(d <= value[i]):
                    return label[i]
            return 'far'

        print('Searching result: ', result)
        ret = {'success': True}
        ret.update({'data': []})
        for shop in result:
            ret['data'].append({
                'shop_name': shop[0].shop_name,
                'category': shop[0].type,
                'distance': getDis(shop[1]),
                'SID': shop[0].SID
            })
        print(ret)
        return jsonify(ret)

    if message['type'] == 'findItem' :
        print('Asking Items for: ', message)
        items = db.session.query(item_).filter(item_.SID == message['SID']).all()

        ret = {'success': False, 'data': []} 
        for item in items :
            ret['data'].append({
                'content': base64.b64encode(item.content).decode(), 
                'name': item.item_name,
                'price': int(item.price),
                'amount': int(item.amount),
                'PID': item.PID
            })
        return jsonify(ret)
        



@app.route('/nav', methods = ['GET'])
@login_required
def nav():

    userID = session.get('_user_id')

    userInfo = db.session.query(user_).filter(user_.UID == userID).first()
    shopInfo = db.session.query(shop_).filter(shop_.UID == userID).first()
    
    info = {}
    info.update({'userAccount': userInfo.account})
    info.update({'userName': userInfo.name})
    info.update({'userPhone': userInfo.phone})
    info.update({'userLatitude': userInfo.lat})
    info.update({'userLongitude': userInfo.lng})
    info.update({'userBalance': userInfo.balance})
    
    if shopInfo != None:
        print('This user has a shop.')
        info.update({'hasShop': True})
        info['shop'] = {
            'shop_name': shopInfo.shop_name,
            'latitude': shopInfo.lat,
            'longitude': shopInfo.lng,
            'phone': shopInfo.phone,
            'food_category': shopInfo.type
        }
        items = db.session.query(item_).filter(item_.SID == shopInfo.SID).all()
        if len(items) > 0:
            print('This user\'s shop has some items')

            info.update({'hasItem': True})

            info.update({'items': []})
            class tmpItem:
                def __init__(self, PID, item_name, price, content, amount):
                    self.PID = PID
                    self.item_name = item_name
                    self.price = price 
                    self.content = content
                    self.amount = amount
            for item in items:
                print('Add itme: ', item)
                image = base64.b64encode(item.content).decode()
                Item = tmpItem(item.PID, item.item_name, item.price, image, item.amount)
                info['items'].append(Item)
    else :
        print('This user has no shop.')
        info.update({'hasShop': False})
    
    backgroundSet = [
        '/static/images/Ayame.jpg',
        '/static/images/ina.jpg',
        '/static/images/fubuki.png',
        '/static/images/mio.jpg'
    ]
    index = np.random.randint(len(backgroundSet))
    return render_template('nav.html', info = info, myBackground = backgroundSet[index])


@app.route('/sign-up', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("sign-up.html")

    if request.method == 'POST':
        message = request.form
        print(message)
        keys = ['name', 'phone', 'account', 'password', 're-password', 'latitude', 'longitude']
        
        ret = checkEmptyAndValue(message, keys)

        # Check repeat 
        if message['password'] != message['re-password'] :
            ret.update({'re-password': 'Re-password is different from password.'})
            ret.update({'success': False})

        # Check account exists
        data = db.session.query(user_).filter(user_.account == message['account']).first()

        if data != None :
            ret.update({'account': 'The account already exists.'})
            ret.update({'success': False})

        if ret['success'] :
            
            newuser = user_(None, 
                         message['account'],
                         message['name'], 
                         message['password'],
                         message['phone'],
                         message['latitude'],
                         message['longitude'],
                         0)
            
            db.session.add(newuser)
            db.session.commit()
            

        return jsonify(ret)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

app.run(host = 'localhost', port = 5000, debug = True)
