from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import requests

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, POS
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
    order_time = datetime.utcnow()
    tz_utc8 = timezone(timedelta(hours=8))
    local_dt = order_time.astimezone(tz_utc8)
    time = local_dt.strftime("%Y/%m/%d %H:%M:%S")

    if not desk.token:
        uuid = uuid4().hex[:12]
        desk.token = uuid
        desk.first_order_time = order_time
        db.session.commit()
    else:
        uuid = desk.token
    order = Order(staff=staff, desk=desk, token=uuid, order_time=order_time)
    db.session.add(order)

    pos_infos = {}

    pos_machs = POS.query.filter(POS.ip!=None).all()
    for pos in pos_machs:
        pos_infos[pos.pos_id] = {'ip':pos.ip, 'split':pos.split, 'products':[]}

    _max_len = 0
    for p_id in products:
        product = Product.query.get(p_id)
        quantity = products[p_id]['num']
        if len(product.p_name) > _max_len:
            _max_len = len(product.p_name)

        for pos_id in product.pos_machs:
            if pos_id in pos_infos:
                pos_infos[pos_id]['products'].append([product.p_name, product.price, quantity])

        order_product = OrderProduct(quantity=quantity)
        order_product.product = product
        order_product.order = order
        db.session.add(order_product)

    for pos_id in pos_infos:
        print_products(uuid, time, desk.d_name, staff.s_name, pos_infos[pos_id], _max_len)

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


def print_products(uuid, time, d_name, s_name, pos_info, _max_len):
    name_field_len = 14
    price_field_len = 7
    total_price_field_len = 8

    url = 'http://'+ pos_info['ip'] +'/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000'
    data ='<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
            <s:Body>\
                <epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
                <text lang="zh-hant"/>'
    
    if pos_info['split']:
        for product_info in pos_info['products']:
            p_name = product_info[0]
            for count in range(product_info[2]):
                data = (data +'<text width="2" height="2"/>\
                    <text>桌號：'+d_name+'&#10;</text>'
                    +'<text>' + p_name + ' '*(12-len(p_name)) 
                    +'x1'+'&#10;</text><cut/>')
    else:
        data = (data +'<text width="2" height="2"/>\
                        <text>桌號：'+d_name+'&#10;</text>\
                        <text width="1" height="1"/>\
                        <feed unit="24"/>\
                        <text>時間：'+time+'&#10;訂單編號：'+uuid+'&#10;</text>\
                        <text>開單人員：'+s_name+'&#10;</text>\
                        <text>---------------------------------------------&#10;</text>')
        for product_info in pos_info['products']:
            p_name = product_info[0]
            price = str(product_info[1])
            total_price = str(product_info[1] * product_info[2])

            data = (data+'<text>' + p_name + ' '*(name_field_len-_max_len) + '  '*(_max_len-len(p_name)) 
                    +'x '+ str(product_info[2]) 
                    + ' '*(price_field_len-len(price)) + price
                    + ' '*(total_price_field_len-len(total_price)) + total_price +'&#10;</text>')
        data = data + '<cut/>'

    data = data + '</epos-print>\
            </s:Body>\
        </s:Envelope>'

    headers = {'Content-Type':'text/xml; charset=utf-8', 'If-Modified-Since':'Thu, 01 Jan 1970 00:00:00 GMT',
        'SOAPAction': '""'}
    print('******ip:'+pos_info['ip']+'******')
    print(data)
    res = requests.post(url, data=data.encode(), headers=headers)
    print(res.status_code)
    if res.status_code != 200:
        tree = ElementTree.fromstring(res.content)
        status = tree[0][0].get('status')
