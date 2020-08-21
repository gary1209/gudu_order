from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime

from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, Staff, POS
from utils import login_required, su_required, json_err, time_translate
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
    return render_template('checkout_open.html', desks_info=desks_info)


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
            'order_products': order.order_products
        })

    return render_template('checkout.html', desk=desk, details=details)


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

    try:
        checkout = Checkout(token=uuid, staff=staff, total_price=desk.price,
                            note=note, desk_name=desk.name)
        db.session.add(checkout)
        ip = POS.query.get(1).ip
        # only pos machine at the checkout counter prints the checkout info
        print_bill(ip, uuid, time, desk.name, staff.name, checkout_info, desk.price)
        db.session.commit()
    except Exception as e:
        print(e)
        return json_err('cannot add new checkout record')
    except PrinterError as e:
        return json_err(e)
    else:
        desk.token = None
        desk.occupied = False
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
                           checkout_infos=checkout_infos)


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
                           s_name=s_name, details=details)


def print_bill(ip, uuid, time, d_name, s_name, checkout_info, check_price):
    name_field_len = 12
    name_len_max = 6
    price_field_len = 7
    total_price_field_len = 8

    url = 'http://' + ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000'
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
<s:Body>\
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
<text lang="zh-hant"/>\
<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<text width="1" height="1"/>\
<feed unit="24"/>\
<text>時間：{}&#10;訂單編號：{}&#10;</text>\
<text>結帳人員：{}&#10;</text>\
<text>=============================================&#10;</text>\
<text width="1" height="2"/>\
'.format(d_name, time, uuid, s_name)


    total_quantity = 0
    for idx, order_products in enumerate(checkout_info):
        if idx is not 0:
            data = data + '<text width="1" height="1"/>\
<text>---------------------------------------------&#10;</text>\
<text width="1" height="2"/>'
        for op in order_products:
            p_name = op.product_name
            price = str(op.product_price).rjust(price_field_len)
            num = op.quantity
            total_price = op.price
            total_quantity = total_quantity + num
            if num < 0:
                p_name = '取消一'+p_name
            if len(p_name) > name_len_max:
                data = data + '<text>{name_pre}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
<text>{name_post}&#10;</text>\
'.format(name_pre=p_name[:name_len_max], space='  '*6, num=num,
         price=price, total=str(op.price).rjust(total_price_field_len), name_post=p_name[name_len_max:])

            else:
                data = data + '<text>{name}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
'.format(name=p_name, space='  '*(name_field_len-len(p_name)), num=num, price=price,
         total=str(op.price).rjust(total_price_field_len))

    data = data + '<text width="1" height="1"/>\
<text>=============================================&#10;</text>\
<text width="2" height="2"/>\
<text>&lt;共{}份&gt;&#10;</text>\
<feed unit="24"/>\
<text>合計：{}&#10;</text><cut/>\
</epos-print>\
</s:Body>\
</s:Envelope>'.format(total_quantity, check_price)


    headers = {'Content-Type': 'text/xml; charset=utf-8', 'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'SOAPAction': '""'}
    res = requests.post(url, data=data.encode(), headers=headers)
    print(res.status_code)
    if res.status_code != 200:
        tree = ElementTree.fromstring(res.content)
        status = tree[0][0].get('status')
        raise(PrinterError(pos_error(status)))
