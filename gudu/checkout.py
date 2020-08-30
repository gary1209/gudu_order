from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime
import xml.etree.ElementTree as ET

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, Staff, POS
from utils import login_required, su_required, json_err, time_translate
from utils import pos_error, save_printer_status, print_bill_format
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
        desks_info.append({'d_id': d.id, 'd_name': d.name})
    return render_template('checkout_open.html', desks_info=desks_info, staff=staff)


@app.route('/<int:d_id>', strict_slashes=False)
@login_required
@su_required
def checkout_page(d_id, staff):
    desk = Desk.query.get(d_id)
    token = desk.token
    orders = desk.orders
    details = []
    for order in orders:
        time = time_translate(order.order_time)
        details.append({
            'staff': order.staff.name,
            'time': time,
            'order_products': order.order_products,
            'note': order.note
        })

    pos_working = config.checkout_pos_working
    return render_template('checkout.html', desk=desk, details=details,
        pos_working=pos_working, staff=staff)


@app.route('/<int:d_id>', methods=['POST'], strict_slashes=False)
@login_required
@su_required
def checkout(d_id, staff):
    note = request.json['note']

    desk = Desk.query.get(d_id)
    uuid = desk.token
    if not uuid:
        abort(403)

    orders = desk.orders
    checkout_info = []
    time = time_translate(datetime.utcnow())
    for order in orders:
        order.status = True
        order_products = order.order_products
        checkout_info.append(order_products)

    checkout = Checkout(token=uuid, staff=staff, total_price=desk.price,
                            note=note, desk_name=desk.name)
    try:
        pos = POS.query.get(1)
        # only pos machine at the checkout counter prints the checkout info
        print_bill(pos, checkout, checkout_info, desk.price)
    except Exception as e:
        checkout.printed = False
        return json_err(str(e))
    finally:
        db.session.add(checkout)
        desk.token = None
        desk.occupied = False
        db.session.commit()
    if not config.checkout_pos_working:
        return {'state': 'printer error'}
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
        week = now.strftime("%Y-%W")
        week_dt = datetime.strptime(week+'-1', "%Y-%W-%w")
        checkouts = Checkout.query.filter(Checkout.checkout_time > week_dt).all()
    else:
        month = now.strftime("%Y-%m")
        month_dt = datetime.strptime(month, "%Y-%m")
        checkouts = Checkout.query.filter(Checkout.checkout_time > month_dt).all()

    checkout_infos = []
    money = 0
    for c in checkouts:
        money = money + c.total_price
        time = time_translate(c.checkout_time)
        checkout_infos.append({'desk_name': c.desk_name, 'time': time, 'token': c.token})

    return render_template('checkout_history.html', type=duration, money=money,
                           checkout_infos=checkout_infos, staff=staff)


@app.route('/history/info/<token>', strict_slashes=False)
@login_required
@su_required
def checkout_history_info_page(token, staff):
    checkout = Checkout.query.get(token)
    s_name = Staff.query.get(checkout.staff_id).name
    orders = Order.query.filter(Order.token == token).all()
    details = []
    checkout_time = time_translate(checkout.checkout_time)

    for order in orders:
        time = time_translate(order.order_time)
        details.append({
            'staff': order.staff.name,
            'time': time,
            'order_products': order.order_products,
            'note': order.note})

    return render_template('checkout_history_info.html',
                           checkout=checkout, time=checkout_time,
                           s_name=s_name, details=details, staff=staff)


def print_bill(pos, checkout, checkout_info, check_price):
    uuid = checkout.token
    time = checkout.checkout_time
    d_name = checkout.desk_name
    s_name = checkout.staff.name

    data = print_bill_format(uuid, time, d_name, s_name, checkout_info, check_price)

    url = 'http://' + pos.ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=30000'
    headers = {'Content-Type': 'text/xml; charset=utf-8', 'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'SOAPAction': '""'}
    try:
        res = requests.post(url, data=data.encode(), headers=headers)
    except (Exception, OSError) as e:
        config.checkout_pos_working = False
        save_printer_status(dict(checkout_pos_working=config.checkout_pos_working, 
            order_pos_working=config.order_pos_working))
        pos.error = str(e)
        db.session.commit()

    if res.status_code is 200:
        tree = ET.fromstring(res.content)
        success = tree[0][0].get('success')
        if success is not 'false':
            status = tree[0][0].get('status')
            if not int(status) & 2:
                config.checkout_pos_working = False
                checkout.printed = False
                pos.error = pos_error(status)
            else:
                config.checkout_pos_working = True
                pos.error = ""
            save_printer_status(dict(checkout_pos_working=config.checkout_pos_working, 
                order_pos_working=config.order_pos_working))
        db.session.commit()
