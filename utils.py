# from telnetlib import SE
# from requests import Session, session
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""
create table user (
	UID INT AUTO_INCREMENT PRIMARY KEY,
    account varchar(64) NOT NULL UNIQUE, 
    name varchar(128) NOT NULL,
    password varchar(256) NOT NULL, 
   	phone DECIMAL(10, 0),
    lat DECIMAL(10, 8) NOT NULL CHECK(lat >= -90.0 and lat <= 90.0),
    lng DECIMAL(11, 8) NOT NULL CHECK(lat >= -180.0 and lat <= 180.0)
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

    def __init__(self, UID, account, name, password, phone, lat, lng):
        self.UID = UID
        self.account = account
        self.name = name
        self.password = password
        self.phone = phone
        self.lat = lat
        self.lng = lng


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
    phone = db.Column(db.NUMERIC(10, 0))
    type = db.Column(db.String(256))

    def __init__(self, SID, UID, shop_name, lat, lng, phone, type):
        self.SID = SID
        self.UID = UID
        self.shop_name = shop_name
        self.lat = lat
        self.lng = lng
        self.phone = phone
        self.type = type


"""
create table item (
    PID INT AUTO_INCREMENT PRIMARY KEY,
    SID INT NOT NULL, 
    item_name varchar(256) NOT NULL,
    price numeric(20, 0) NOT NULL CHECK(price >= 0),
    content varchar(256) NOT NULL,
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
    TID = db.Column(db.Integer, primary_key = True)
    UID = db.Column(db.Integer)
    type = db.Column(db.String(16))
    amount = db.Column(db.NUMERIC(20, 0))
    trade_time = db.Column(db.DateTime)

    def __init__(self, TID, UID, type, amount, trade_time):
        self.TID = TID
        self.UID = UID
        self.type = type
        self.amount = amount
        self.trade_time = trade_time


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
    amount = amount = db.Column(db.NUMERIC(20, 0))

    def __init__(self, OID, TID, amount):
        self.OID = OID
        self.TID = TID
        self.amount = amount

# check is float
def isFloat(s) :
    try:
        float(s)
        return True
    except ValueError:
        return False






