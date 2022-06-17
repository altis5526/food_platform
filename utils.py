
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
import re

db = SQLAlchemy()

"""
create table user (
	UID INT AUTO_INCREMENT PRIMARY KEY,
    account varchar(64) NOT NULL UNIQUE, 
    name varchar(128) NOT NULL,
    password varchar(256) NOT NULL, 
   	phone DECIMAL(10, 0),
    lat DECIMAL(10, 8) NOT NULL CHECK(lat >= -90.0 and lat <= 90.0),
    lng DECIMAL(11, 8) NOT NULL CHECK(lat >= -180.0 and lat <= 180.0),
    balance NUMERIC(20, 0) DEFAULT 0
);
"""
class user_(db.Model):
    __tablename__ = 'user'
    UID = db.Column(db.Integer, primary_key = True)
    account = db.Column(db.String(64))
    name = db.Column(db.String(128))
    password = db.Column(db.String(256))
    phone = db.Column(db.NUMERIC(10, 0))
    lat = db.Column(db.NUMERIC(10, 8))
    lng = db.Column(db.NUMERIC(11, 8))
    position = db.Column(db.String(256))
    balance = db.Column(db.NUMERIC(20, 0))

    def __init__(self, UID, account, name, password, phone, lat, lng, balance):
        self.UID = UID
        self.account = account
        self.name = name
        self.password = password
        self.phone = phone
        self.lat = lat
        self.lng = lng
        self.balance = balance
        self.position = 'POINT(%.6f %.6f)' % (float(lng), float(lat))

"""
create table shop (
    SID INT AUTO_INCREMENT PRIMARY KEY, 
    UID INT NOT NULL, 
    shop_name varchar(64) NOT NULL,
    lat DECIMAL(10, 8) NOT NULL CHECK(lat >= -90.0 and lat <= 90.0),
    lng DECIMAL(11, 8) NOT NULL CHECK(lat >= -180.0 and lat <= 180.0),
    phone DECIMAL(10, 0) NOT NULL,
    type varchar(256) NOT NULL,
    FOREIGN KEY (UID) REFERENCES user (UID)
);
"""
class shop_(db.Model):
    __tablename__ = 'shop'
    SID = db.Column(db.Integer, primary_key = True)
    UID = db.Column(db.Integer)
    shop_name = db.Column(db.String(64))
    lat = db.Column(db.NUMERIC(10, 8))
    lng = db.Column(db.NUMERIC(11, 8))
    position = db.Column(db.String(256))
    phone = db.Column(db.NUMERIC(10, 0))
    type = db.Column(db.String(256))

    def __init__(self, SID, UID, shop_name, lat, lng, phone, type):
        self.SID = SID
        self.UID = UID
        self.lat = lat
        self.lng = lng
        self.type = type
        self.phone = phone
        self.shop_name = shop_name
        self.position = 'POINT(%.6f %.6f)' % (float(lng), float(lat))


"""
create table item (
    PID INT AUTO_INCREMENT PRIMARY KEY,
    SID INT NOT NULL, 
    item_name varchar(256) NOT NULL,
    price numeric(20, 0) NOT NULL CHECK(price >= 0),
    content LONGBOLB NOT NULL,
    amount INT DEFAULT 0,
    FOREIGN KEY (SID) REFERENCES shop (SID)  
);
"""
class item_(db.Model):
    __tablename__ = 'item'
    PID = db.Column(db.Integer, primary_key = True)
    SID = db.Column(db.Integer)
    item_name = db.Column(db.String(256))
    price = db.Column(db.NUMERIC(20, 0))
    content = db.Column(db.LargeBinary)
    amount = db.Column(db.Integer)

    def __init__(self, PID, SID, item_name, price, content, amount):
        self.PID = PID
        self.SID = SID
        self.item_name = item_name
        self.price = price
        self.content = content
        self.amount = amount



"""
create table order_instance (
    OID INT AUTO_INCREMENT PRIMARY KEY, 
    UID INT NOT NULL,
    SID INT NOT NULL,
    state varchar(16) NOT NULL, 
    create_time TIMESTAMP(6) DEFAULT NOW(), 
    done_time TIMESTAMP(6) DEFAULT NOW(), 
    distance DOUBLE NOT NULL, 
    amount numeric(20, 0) NOT NULL CHECK(amount >= 0),
    type varchar(16),
    FOREIGN KEY (UID) REFERENCES user(UID),
    FOREIGN KEY (SID) REFERENCES shop(SID)
);
"""
class order_instance_(db.Model):
    __tablename__ = 'order_instance'
    OID = db.Column(db.Integer, primary_key = True)
    UID = db.Column(db.Integer)
    SID = db.Column(db.Integer)
    state = db.Column(db.String(16))
    create_time = db.Column(db.DateTime)
    done_time = db.Column(db.DateTime)
    distance = db.Column (db.Float)
    amount = db.Column(db.NUMERIC(20, 0))
    type = db.Column(db.String(16))

    def __init__(self, OID, UID, SID, state, creat_time, done_time, distance, amount, type):
        self.OID = OID
        self.UID = UID
        self.SID = SID
        self.state = state
        self.create_time = creat_time
        self.done_time = done_time
        self.distance = distance
        self.amount = amount
        self.type = type        



"""
create table trade (
    TID INT AUTO_INCREMENT PRIMARY KEY,
    UID INT NOT NULL,
    type varchar(16),
    amount numeric(20, 0) NOT NULL CHECK(amount >= 0),
    trade_time TIMESTAMP(6) DEFAULT NOW(),
    FOREIGN KEY (UID) REFERENCES user(UID)
);
"""
class trade_(db.Model):
    __tablename__ = 'trade'
    TID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    UID = db.Column(db.Integer)
    type = db.Column(db.String(16))
    amount = db.Column(db.NUMERIC(20, 0))
    trade_time = db.Column(db.DateTime)
    trader = db.Column(db.String(128))

    def __init__(self, TID, UID, type, amount, trade_time, trader):
        self.TID = TID
        self.UID = UID
        self.type = type
        self.amount = amount
        self.trade_time = trade_time
        self.trader = trader


"""
create table order_content (
    OID INT NOT NULL,
    PID INT NOT NULL,
    amount numeric(20, 0) NOT NULL CHECK(amount >= 0),
    PRIMARY KEY (OID, PID),
    FOREIGN KEY (OID) REFERENCES order_instance(OID),
    FOREIGN KEY (PID) REFERENCES item(PID)
);
"""
class order_content_(db.Model):
    __tablename__ = 'order_content'
    OID = db.Column(db.Integer, primary_key = True)
    PID = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.NUMERIC(20, 0))

    def __init__(self, OID, PID, amount):
        self.OID = OID
        self.PID = PID
        self.amount = amount

# empty message for different attribute
empty_message = {
    
    # For user 
    'name': 'Name can\'t be empty.',
    'phone': 'Please fill in your phone number.',
    'account': 'Account can\'t be empty.',
    'password': 'Please fill in your password.',
    're-password': 'Please repeat your password.',
    'latitude': 'latitude can\'t be empty', 
    'longitude': 'longitude can\'t be empty',

    # For shop
    'shop_name': 'Shop name can\'t be empty.',

    # For Item
    'meal_name': 'Meal name can\'t be empty.',
    'price': 'Price can\'t be empty.',
    'amount': 'Quantity can\'t be empty.',
    'myFile': 'You should at least upload an image'
}

# error message for different attribute
error_message = {
    # For user
    'name': 'Your name must be a string with length less than 128 and contains only latin letters and numbers.',
    'phone': 'Your phone number must be a 10-digit number.',
    'account': 'Your account be a string with length less than 64 and contains only latin latters and numbers.',
    'latitude': 'Latitude must be a number between -90 and 90.', 
    'longitude': 'Longitude must be a number between -180 and 180.',

    # For shop
    'shop_name': 'Your shop name must be a string with length less than 64.',
    'food_category': 'Your food category must be a string with length than 256.',
    
    # For Item
    'meal_name': '',
    'price': 'Your price must contain only non-negative numbers.',
    'amount': 'Your quantity must contain only non-negative numbers.'
}

# pattern check for different attribute
Patterns = {
    # For user
    'name': lambda s : re.match('^[A-Za-z]+$', s) != None and len(s) < 128,
    'phone': lambda s : re.match('^\d{10}$', s) != None,
    'account': lambda s : re.match('^[a-zA-Z0-9]+$', s) != None and len(s) < 64,
    'latitude': lambda s : isFloat(s) and -90 <= float(s) and 90 >= float(s),
    'longitude': lambda s : isFloat(s) and -180 <= float(s) and 180 >= float(s),

    # For shop
    'shop_name': lambda s : len(s) < 64,
    'food_category': lambda s: len(s) < 256,

    # For Item
    'meal_name': lambda s: len(s) != 0,
    'price': lambda s : isInteger(s) and (int(s) >= 0),
    'amount': lambda s : isInteger(s) and (int(s) >= 0),
}

def checkEmptyAndValue(message, keys):
    ret = {'success': True}
    for key in keys :
        ret.update({key: ''})
    # Check empty
    for key in keys:
        if (key not in message.keys() or len(message[key]) == 0) and key in empty_message.keys():
            ret.update({key: empty_message[key]})
            ret.update({'success': False})

    # check value
    for key in keys:
        if ret[key] == '' and key in Patterns.keys() and not Patterns[key](message[key]) :
            ret.update({key: error_message[key]})
            ret.update({'success': False})

    return ret

# check is float
def isFloat(s) :
    try:
        float(s)
        return True
    except ValueError:
        return False

# check is Integer
def isInteger(s) :
    try:
        int(s)
        return True
    except ValueError:
        return False
