from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import requests

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, POS
from utils import login_required, su_required, json_err, time_translate

app = Blueprint('order', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def order_page(staff):
    categories = Category.query.order_by(Category.id).all()
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
    note = request.json['note']

    desk = Desk.query.get(d_id)
    uuid = None
    order_time = datetime.utcnow()
    dt = order_time.replace(tzinfo=timezone.utc)
    tz_utc8 = timezone(timedelta(hours=8))
    local_dt = dt.astimezone(tz_utc8)
    time = local_dt.strftime("%Y/%m/%d %H:%M:%S")

    if not desk.token:
        uuid = uuid4().hex[:12]
        desk.token = uuid
        desk.occupied = True
        db.session.commit()
    else:
        uuid = desk.token
    order = Order(staff=staff, desk=desk, token=uuid,
                  order_time=order_time, note=note)
    db.session.add(order)

    pos_infos = {}

    pos_machs = POS.query.filter(POS.ip != '').all()
    for pos in pos_machs:
        pos_infos[pos.id] = {'ip': pos.ip, 'split': pos.split, 'note': note, 'products': []}

    for p_id in products:
        product = Product.query.get(p_id)
        quantity = products[p_id]['num']

        for pos_id in product.pos_machs:
            if pos_id in pos_infos:
                pos_infos[pos_id]['products'].append([product.name, product.price, quantity])

        order_product = OrderProduct(quantity=quantity)
        order_product.product = product
        order_product.order = order
        db.session.add(order_product)

    print(pos_infos)
    for pos_id in pos_infos:
        # pos machine at the checkout counter won't print the order info
        if len(pos_infos[pos_id]['products']) != 0 and pos_id != 1:
            print_products(uuid, time, desk.name, staff.name, pos_infos[pos_id])

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
            quantity = OrderProduct.query.filter(OrderProduct.order == order and OrderProduct.product == p).first().quantity
            details.append((p.name, p.price, quantity, p.price*quantity))

    return {'details': details}


def print_products(uuid, time, d_name, s_name, pos_info):
    name_field_len = 14
    price_field_len = 7
    total_price_field_len = 8

    url = 'http://' + pos_info['ip'] + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000'
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
            <s:Body>\
                <epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
                <text lang="zh-hant"/>'

    if pos_info['split']:
        for product_info in pos_info['products']:
            p_name = product_info[0]
            for count in range(product_info[2]):
                data = data + '<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<text>{}x1&#10;</text><cut/>'.format(d_name, p_name.rjust(12))

    else:
        data = data + '<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<text width="1" height="1"/>\
<feed unit="24"/>\
<text>時間：{}&#10;訂單編號：{}&#10;</text>\
<text>開單人員：{}&#10;</text>\
<text>---------------------------------------------&#10;</text>\
'.format(d_name, time, uuid, s_name)

        total_quantity = 0
        order_price = 0
        for product_info in pos_info['products']:
            p_name = product_info[0]
            num = product_info[2]
            space = '  '*(13-len(p_name))
            price = str(product_info[1]).ljust(7)
            total_price = product_info[1] * product_info[2]
            data = data + '<text>{name}{space}x {num}{price}{total}&#10;</text>\
'.format(name=p_name, space=space, num=num, price=price, total=str(total_price).ljust(8))

            total_quantity = total_quantity + product_info[2]
            order_price = order_price + total_price

        data = data + '<text>---------------------------------------------&#10;</text>\
<text>備註：{}&#10;</text>\
<text>&lt;共{}份&gt;&#10;</text>\
<text width="2" height="2"/>\
<text>小計：{}&#10;</text>\
<cut/>'.format(pos_info['note'], total_quantity, order_price)

    data = data + '</epos-print>\
            </s:Body>\
        </s:Envelope>'

    headers = {'Content-Type': 'text/xml; charset=utf-8', 'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'SOAPAction': '""'}
    print('******ip:'+pos_info['ip']+'******')
    print(data)
    res = requests.post(url, data=data.encode(), headers=headers)
    print(res.status_code)
    if res.status_code != 200:
        tree = ElementTree.fromstring(res.content)
        status = tree[0][0].get('status')
