from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, Staff, POS
from utils import login_required, su_required, json_err
import requests

app = Blueprint('checkout', __name__)
db = config.db


@app.route('/', strict_slashes=False)
@login_required
@su_required
def checkout_open_page(staff):
    desks = Desk.query.filter(Desk.token != None).all()
    desks_info = []
    for d in desks:
        dt = d.first_order_time.replace(tzinfo=timezone.utc)
        tz_utc8 = timezone(timedelta(hours=8))
        local_dt = dt.astimezone(tz_utc8)
        time = local_dt.strftime("%Y/%m/%d, %H:%M:%S")
        desks_info.append({'d_id': d.id, 'd_name': d.name, 'time': time})
    return render_template('checkout_open.html', desks_info=desks_info)


@app.route('/<int:d_id>', strict_slashes=False)
@login_required
@su_required
def checkout_page(d_id, staff):
    desk = Desk.query.get(d_id)
    token = desk.token
    orders = desk.orders
    details = []
    total_price = 0
    for order in orders:
        for op in order.order_products:
            details.append((op.product, op.quantity))
            total_price = total_price + op.quantity * op.product.price

    return render_template('checkout.html', desk=desk, total_price=total_price, details=details)


@app.route('/<int:d_id>', methods=['POST'], strict_slashes=False)
@login_required
@su_required
def checkout(d_id, staff):
    check_price = request.json['total_price']
    note = request.json['note']

    desk = Desk.query.get(d_id)
    uuid = desk.token
    if not uuid:
        abort(403)

    orders = desk.orders
    checkout_info = []
    dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    tz_utc8 = timezone(timedelta(hours=8))
    local_dt = dt.astimezone(tz_utc8)
    time = local_dt.strftime("%Y/%m/%d %H:%M:%S")
    for order in orders:
        order.status = True
        order_products = order.order_products
        checkout_info.append(order_products)

    try:
        checkout = Checkout(token=uuid, staff=staff, total_price=check_price,
                            note=note, desk_name=desk.name)
        db.session.add(checkout)
        ip = POS.query.get(1).ip
        print_bill(ip, uuid, time, desk.name, staff.name, checkout_info, check_price)
        db.session.commit()
    except Exception as e:
        print(e)
        return json_err('cannot add new checkout record')
    else:
        desk.token = None
        db.session.commit()
    return {'state': 'ok'}


@app.route('/history/<duration>', strict_slashes=False)
@login_required
@su_required
def checkout_history_page(duration, staff):
    now = datetime.utcnow()
    checkouts = []
    if duration == 'today':
        today = now.strftime("%Y-%m-%d")
        today_dt = datetime.strptime(today, "%Y-%m-%d")
        checkouts = Checkout.query.filter(Checkout.checkout_time > today_dt).all()
    elif duration == 'week':
        week = now.strftime("%Y %W")
        week_dt = datetime.strptime(week, "%Y %W")
        checkouts = Checkout.query.filter(Checkout.checkout_time > week_dt).all()
    else:
        month = now.strftime("%Y-%m")
        month_dt = datetime.strptime(month, "%Y-%m")
        checkouts = Checkout.query.filter(Checkout.checkout_time > month_dt).all()

    checkout_infos = []
    tz_utc8 = timezone(timedelta(hours=8))
    for c in checkouts:
        dt = c.checkout_time.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(tz_utc8)
        time = local_dt.strftime("%Y/%m/%d, %H:%M:%S")
        checkout_infos.append({'desk_name': c.desk_name, 'time': time, 'token': c.token})

    return render_template('checkout_history.html', type=duration, checkout_infos=checkout_infos)


@app.route('/history/info/<token>', strict_slashes=False)
@login_required
@su_required
def checkout_history_info_page(token, staff):
    checkout = Checkout.query.get(token)
    s_name = Staff.query.get(checkout.staff_id).s_name
    orders = Order.query.filter(Order.token == token).all()
    details = []

    for order in orders:
        for op in order.order_products:
            details.append((op.product, op.quantity))

    return render_template('checkout_history_info.html', d_name=checkout.desk_name, s_name=s_name,
                           details=details, total_price=checkout.total_price, note=checkout.note)


def print_bill(ip, uuid, time, d_name, s_name, checkout_info, check_price):
    name_field_len = 14
    price_field_len = 7
    total_price_field_len = 8

    url = 'http://' + ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000'
    data = ('<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
                <s:Body>\
                    <epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
                    <text lang="zh-hant"/>\
                    <text width="2" height="2"/>\
                    <text>桌號：'+d_name+'&#10;</text>\
                    <text width="1" height="1"/>\
                    <feed unit="24"/>\
                    <text>時間：'+time+'&#10;訂單編號：'+uuid+'&#10;</text>\
                    <text>結帳人員：'+s_name+'&#10;</text>\
                    <text>=============================================&#10;</text>')

    total_quantity = 0
    for idx, order_products in enumerate(checkout_info):
        if idx is not 0:
            data = data + '<text>---------------------------------------------&#10;</text>'
        for order_product in order_products:
            name = order_product.product.name
            price = str(order_product.product.price)
            quantity = order_product.quantity
            total_quantity = total_quantity + quantity
            total_price = str(order_product.product.price * quantity)
            data = (data + '<text>' + name + ' '*(name_field_len-12) + '  '*(12-len(name))
                    +'x '+ str(quantity)
                    + ' '*(price_field_len-len(price)) + price
                    + ' '*(total_price_field_len-len(total_price)) + total_price + '&#10;</text>')

    data = (data + '<text>=============================================&#10;</text>\
                    <text>&lt;共' + str(total_quantity) + '份&gt;&#10;</text>\
                    <text width="2" height="2"/>\
                    <text>合計：' + str(check_price) + '&#10;</text><cut/>\
                    </epos-print>\
                </s:Body>\
            </s:Envelope>')

    headers = {'Content-Type': 'text/xml; charset=utf-8', 'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'SOAPAction': '""'}
    res = requests.post(url, data=data.encode(), headers=headers)
    print(res.status_code)
    if res.status_code != 200:
        tree = ElementTree.fromstring(res.content)
        status = tree[0][0].get('status')
        # [TODO] parse error
