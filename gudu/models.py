from datetime import datetime, timedelta


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from config import config

db = config.db


class Staff(db.Model):
    __tablename__ = 'Staff'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', backref='staff')
    checkouts = db.relationship('Checkout', backref='staff')

    @property
    def is_su(self):
        return self.is_superuser is True


class Desk(db.Model):
    __tablename__ = 'Desk'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(45), nullable=False, unique=True)
    token = db.Column(db.String, unique=True)
    first_order_time = db.Column(db.DateTime)
    orders = db.relationship('Order',
        primaryjoin="and_(Order.desk_id==Desk.id, Order.token==Desk.token)",
        backref='desk', order_by='Order.id')


class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(45), nullable=False)

    products = db.relationship('Product', backref='category')


class Product(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(45), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('Category.id'))
    available = db.Column(db.Boolean, default=True)
    pos_machs = db.Column(db.JSON)

    orders = association_proxy("order_products", "order")


class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.Boolean, default=False)
    order_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    staff_id = db.Column(db.Integer, db.ForeignKey('Staff.id'), nullable=False)
    desk_id = db.Column(db.Integer, db.ForeignKey('Desk.id'), nullable=False)
    # 每組客人有不同token, 用來區分是哪組客人
    token = db.Column(db.String, nullable=False)
    note = db.Column(db.String)

    products = association_proxy("order_products", "product")

    # 一張單的金額
    @property
    def order_price(self):
        return OrderProduct.total_price(order=self)

    # # 同組客人所有單的金額
    # @classmethod
    # def total_price(cls, token):
    #     orders = cls.query.filter(cls.token == token).all()
    #     return sum(list(map(lambda x: x.order_price, orders))) 


# this is for the many-to-many relationship between product and order
class OrderProduct(db.Model):
    __tablename__ = 'OrderProduct'
    order_id = db.Column(db.Integer, db.ForeignKey('Order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship(Product, backref="order_products")
    order = db.relationship(Order, backref="order_products")

    @classmethod
    def total_price(cls, order):
        records = cls.query.filter(cls.order == order).all()
        if len(records) != 0:
            return sum(list(map(lambda x: x.product.price * x.quantity, records)))
        else:
            return 0


# 結帳時才有這筆紀錄
class Checkout(db.Model):
    __tablename__ = 'Checkout'
    token = db.Column(db.String, primary_key=True, autoincrement=False)
    checkout_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    staff_id = db.Column(db.Integer, db.ForeignKey('Staff.id'), nullable=False)
    desk_name = db.Column(db.String(45), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String) 


class POS(db.Model):
    __tablename__ = 'POS'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(45))
    ip = db.Column(db.String(27))
    split = db.Column(db.Boolean, default=False)