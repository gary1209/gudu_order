from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout
from utils import login_required, su_required, json_err

app = Blueprint('order', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def order_page(staff):
    categories = Category.query.all()
    _cate = {}
    for c in categories:
        _cate[c] = c.products

    desks = Desk.query.all()
    return render_template('order.html', categories=_cate, desks=desks)

@app.route('/', methods=['POST'], strict_slashes=False)
@login_required
def order(staff):
    d_id = request.json['d_id']
    products = request.json['products']

    desk = Desk.query.get(d_id)
    uuid = None
    if not desk.token:
        uuid = uuid4().hex
        desk.token = uuid
        desk.first_order_time = datetime.utcnow()
        db.session.commit()
    else:
        uuid = desk.token
    order = Order(staff=staff, desk=desk, token=uuid)
    db.session.add(order)

    for p_id in products:
        product = Product.query.get(p_id)
        order_product = OrderProduct(quantity=products[p_id]['num'])
        order_product.product = product
        order_product.order = order
        db.session.add(order_product)
    db.session.commit()
    return 'ok'

@app.route('/check', methods=['POST'], strict_slashes=False)
@login_required
def check_desk_orders(staff):
    d_id = request.json['d_id']
    desk = Desk.query.get(d_id)

    if not desk:
        abort(403)

    orders = desk.orders
    details = []
    for order in orders:
        for p in order.products:
            quantity = OrderProduct.query.filter(OrderProduct.order==order and OrderProduct.product==p).first().quantity
            details.append((p.p_name, p.price, quantity, p.price*quantity))

    return {'details':details}

@app.route('/checkout', strict_slashes=False)
@login_required
@su_required
def checkout_page(staff):
    desks = Desk.query.filter(Desk.token != None).all()
    desks_info = []
    for d in desks:
        dt = d.first_order_time.replace(tzinfo=timezone.utc)
        tz_utc8 = timezone(timedelta(hours=8))
        local_dt = dt.astimezone(tz_utc8)
        time = local_dt.strftime("%Y/%m/%d, %H:%M:%S")
        desks_info.append({'d_id': d.d_id, 'd_name': d.d_name, 'time': time})
    return render_template('checkout.html', desks_info=desks_info)


@app.route('/checkout/<int:d_id>', strict_slashes=False)
@login_required
@su_required
def checkout_detail_page(d_id, staff):
    desk = Desk.query.get(d_id)
    token = desk.token
    orders = desk.orders
    details = []
    total_price = 0
    for order in orders:
        for p in order.products:
            quantity = OrderProduct.query.filter(OrderProduct.order==order and OrderProduct.product==p).first().quantity
            details.append((p, quantity))
            total_price = total_price + quantity * p.price
    print(details)
    return render_template('checkout_detail.html', desk=desk, total_price=total_price, details=details)


@app.route('/checkout/<int:d_id>', methods=['POST'], strict_slashes=False)
@login_required
@su_required
def checkout(d_id, staff):
    total_price = request.json['total_price']
    note = request.json['note']

    desk = Desk.query.get(d_id)
    uuid = desk.token
    if not uuid:
        abort(403)

    try:
        checkout = Checkout(token=uuid, staff=staff, total_price=total_price, note=note)
        db.session.add(checkout)
        db.session.commit()
    except Exception as e:
        print(e)
        return json_err('cannot add new checkout record')
    else:
        desk.token = None
        db.session.commit()

    return {'state':'ok'}


def test_order(staff):
    p1 = Product.query.get(1)
    p2 = Product.query.get(2)
    desk = Desk.query.get(1)

    uuid = uuid4().hex
    desk.token = uuid
    db.session.commit()

    order = Order(staff=staff, desk=desk, token=uuid)
    order.products.append(p1)
    order.products.append(p2)
    db.session.add(order)
    db.session.commit()

    return 'ok'


@app.route('/check', methods=['GET'])
@login_required
def test_check_order(staff):
    products = Order.query.first().products
    for p in products:
        print(p.p_name)
    return 'ok'


@app.route('/current_orders', methods=['GET'])
@login_required
def test_check_table_order(staff):
    desk = Desk.query.get(1)
    orders = desk.orders
    for o in orders:
        print(o.o_id)
    return 'ok'