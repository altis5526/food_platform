create DATABASE food_platform;
use food_platform;

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

create table item (
    PID INT AUTO_INCREMENT PRIMARY KEY,
    SID INT NOT NULL, 
    item_name varchar(256) NOT NULL,
    price numeric(20, 0) NOT NULL CHECK(price >= 0),
    content LONGBOLB NOT NULL,
    amount INT DEFAULT 0,
    FOREIGN KEY (SID) REFERENCES shop (SID)  
);

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

create table trade (
    TID INT AUTO_INCREMENT PRIMARY KEY,
    UID INT NOT NULL,
    type varchar(16),
    amount numeric(20, 0) NOT NULL CHECK(amount >= 0),
    trade_time TIMESTAMP(6) DEFAULT NOW(),
    FOREIGN KEY (UID) REFERENCES user(UID)
);

create table order_content (
    OID INT NOT NULL,
    PID INT NOT NULL,
    amount numeric(20, 0) NOT NULL CHECK(amount >= 0),
    PRIMARY KEY (OID, PID),
    FOREIGN KEY (OID) REFERENCES order_instance(OID),
    FOREIGN KEY (PID) REFERENCES item(PID)
);
