from flask import Blueprint, render_template, request, redirect, session
from sqlalchemy import and_
from flask import url_for, jsonify, abort
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import requests
import asyncio
from functools import partial


from config import config
from models import Order, Desk, Product, Category, OrderProduct, Checkout, POS
from utils import login_required, su_required, json_err, time_translate, pos_error, PrinterError

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


@app.route('/<int:d_id>', methods=['GET'], strict_slashes=False)
@login_required
def desk_order_page(d_id, staff):
    categories = Category.query.order_by(Category.id).all()
    _cate = {}
    for c in categories:
        _cate[c] = c.products

    desk = Desk.query.get(d_id)
    if not desk:
        abort(404)
    return render_template('order.html', categories=_cate, desk=desk)


@app.route('/', methods=['POST'], strict_slashes=False)
@login_required
def order(staff):
    '''
        products: [{
            'id': product.id,
            'num': quantity
        }, ...]
    '''
    d_id = request.json['d_id']
    products = request.json['products']
    note = request.json['note']

    desk = Desk.query.get(d_id)
    if not desk:
        abort(403)

    uuid = None
    if not desk.token:
        uuid = uuid4().hex[:12]
        desk.token = uuid
        desk.occupied = True
        db.session.commit()
    else:
        uuid = desk.token

    # check number of cancel products
    cancel_products = list(filter(lambda x: x['num'] < 0, products))
    cancel_pid = list(map(lambda x: int(x['id']), cancel_products))
    error_info = {}
    # 計算每個要取消的商品，之前已經被這組客人點過幾個
    for order in desk.orders:
        for op in order.order_products:
            p_id = op.product.id
            if p_id in cancel_pid:
                if p_id in error_info:
                    error_info[p_id] = error_info[p_id] + op.quantity
                else:
                    error_info[p_id] = op.quantity
    msg = ''
    for p_id in error_info:
        info = list(filter(lambda x: x['id'] is p_id, cancel_products))[0]
        cancel_num = info['num']
        num = error_info[p_id]
        if cancel_num + num < 0:
            msg = msg + '{}目前共點{}個，不可取消{}個\n'.format(info['name'], num, abs(cancel_num))
    if len(msg) > 0:
        return json_err(msg)

    order_time = datetime.utcnow()
    time = time_translate(order_time)
    order = Order(staff=staff, desk=desk, token=uuid,
                  order_time=order_time, note=note)
    db.session.add(order)

    pos_infos = {}
    pos_machs = POS.query.filter(POS.ip != '').all()
    for pos in pos_machs:
        pos_infos[pos.id] = {'ip': pos.ip, 'split': pos.split, 'note': note, 'products': []}

    for p in products:
        product = Product.query.get(p['id'])
        quantity = p['num']

        for pos_id in product.pos_machs:
            if pos_id in pos_infos:
                pos_infos[pos_id]['products'].append([product.name, product.price, quantity])

        order_product = OrderProduct(quantity=quantity)
        order_product.product = product
        order_product.order = order
        db.session.add(order_product)

    exceptions = []
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    tasks = []
    try:
        for pos_id in pos_infos:
            # pos machine at the checkout counter won't print the order info
            if len(pos_infos[pos_id]['products']) != 0 and pos_id != 1:
                data = print_products(uuid, time, desk.name, staff.name, pos_infos[pos_id])
                tasks.append(loop.create_task(send_req(pos_infos[pos_id]['ip'], data)))
        loop.run_until_complete(asyncio.wait(tasks))
    except PrinterError as e:
        exceptions.append(e)
    else:
        db.session.commit()
    finally:
        loop.close()
        if len(exceptions) > 0:
            return json_err(exceptions)
    return {'state': 'ok'}


async def send_req(ip, data):
    url = 'http://' + ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=10000'
    headers = {'Content-Type': 'text/xml; charset=utf-8',
               'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
               'SOAPAction': '""'}
    f = partial(requests.post, url, data=data.encode(), headers=headers)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, f)
    if res.status_code != 200:
        tree = ElementTree.fromstring(res.content)
        status = tree[0][0].get('status')
        raise(PrinterError(pos_error(status)))


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
        for op in order.order_products:
            details.append((op.product.name, op.product.price, op.quantity, op.product.price*op.quantity))

    return {'details': details}


def print_products(uuid, time, d_name, s_name, pos_info):
    name_field_len = 12
    name_len_max = 6
    price_field_len = 7
    total_price_field_len = 8

    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
<s:Body>\
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
<text lang="zh-hant"/>'

    if pos_info['split']:
        for product_info in pos_info['products']:
            p_name = product_info[0]
            num = product_info[2]
            if num > 0:
                for count in range(product_info[2]):
                    data = data + '<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<feed unit="24"/>\
<text>{}x1&#10;</text><cut/>'.format(d_name, p_name.ljust(name_field_len))
            else:
                data = data + '<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<feed unit="24"/>\
<text>（取消）{}x{}&#10;</text><cut/>'.format(d_name, p_name.ljust(8), abs(num))

    else:
        data = data + '<text width="2" height="2"/>\
<text>桌號：{}&#10;</text>\
<text width="1" height="1"/>\
<feed unit="24"/>\
<text>時間：{}&#10;訂單編號：{}&#10;</text>\
<text>開單人員：{}&#10;</text>\
<text>---------------------------------------------&#10;</text>\
<text width="1" height="2"/>\
'.format(d_name, time, uuid, s_name)

        total_quantity = 0
        order_price = 0
        for product_info in pos_info['products']:
            p_name = product_info[0]
            num = product_info[2]
            price = str(product_info[1]).rjust(price_field_len)
            total_price = product_info[1] * product_info[2]
            total_quantity = total_quantity + product_info[2]
            order_price = order_price + total_price

            if num < 0:
                p_name = '取消一'+p_name

            if len(p_name) > name_len_max:
                data = data + '<text>{name_pre}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
<text>{name_post}&#10;</text>\
'.format(name_pre=p_name[:name_len_max], space='  '*6, num=num,
         price=price, total=str(total_price).rjust(total_price_field_len), name_post=p_name[name_len_max:])

            else:
                data = data + '<text>{name}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
'.format(name=p_name, space='  '*(name_field_len-len(p_name)), num=num, price=price,
         total=str(total_price).rjust(total_price_field_len))

        data = data + '<text width="1" height="1"/>\
<text>---------------------------------------------&#10;</text>\
<text width="2" height="2"/>\
<text>備註：{}&#10;</text>\
<feed unit="24"/>\
<text>&lt;共{}份&gt;&#10;</text>\
<feed unit="24"/>\
<text>小計：{}&#10;</text>\
<cut/>'.format(pos_info['note'], total_quantity, order_price)

    data = data + '</epos-print>\
            </s:Body>\
        </s:Envelope>'

    print('******ip:'+pos_info['ip']+'******')
    print(data)
    return data
