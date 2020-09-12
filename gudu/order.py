from flask import Blueprint, render_template, request, redirect, session
from sqlalchemy import and_
from flask import url_for, jsonify, abort
from datetime import datetime, timezone, timedelta
import requests
import asyncio
from functools import partial
import xml.etree.ElementTree as ET


from config import config
from models import Order, Desk, Product, Category, CustomerCount
from models import OrderProduct, Checkout, POS, PrintFailed
from utils import login_required, su_required, json_err, time_translate
from utils import pos_error, save_printer_status, print_order_format

app = Blueprint('order', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
def order_page(staff):
    categories = Category.query.order_by(Category.id).all()
    _cate = []
    for c in categories:
        _cate.append((c, c.products))

    desks = Desk.query.all()
    return render_template('order.html', categories=categories,
        info=_cate, desks=desks, pos_working=POS.order_pos_all_working(), staff=staff)


@app.route('/<int:d_id>', methods=['GET'], strict_slashes=False)
@login_required
def desk_order_page(d_id, staff):
    categories = Category.query.order_by(Category.id).all()
    _cate = []
    for c in categories:
        _cate.append((c, c.products))

    desk = Desk.query.get(d_id)
    if not desk:
        abort(404)
    desks = Desk.query.all()
    return render_template('order.html', categories=categories, staff=staff,
        info=_cate, desk=desk, desks=desks, pos_working=POS.order_pos_all_working())


@app.route('/', methods=['POST'], strict_slashes=False)
@login_required
def order(staff):
    '''
        products: [{
            'id': product.id,
            'num': quantity,
            'price': op.product_price
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
        now = datetime.utcnow()
        today = now.strftime("%Y-%m-%d")
        today_dt = datetime.strptime(today, "%Y-%m-%d")
        count_record = CustomerCount.query.with_for_update(of=CustomerCount).filter_by(date=today_dt).first()
        if not count_record:
            count_record = CustomerCount(date=today_dt)
            db.session.add(count_record)
            db.session.commit()
            uuid = today + '-1'
        else:
            count = count_record.count + 1
            count_record.count = count
            db.session.commit()
            uuid = today + '-{}'.format(count)

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
    for info in cancel_products:
        p_id = info['id']
        cancel_num = info['num']
        if p_id in error_info:
            num = error_info[p_id]
            if cancel_num + num < 0:
                msg = msg + '{}目前共點{}個，不可取消{}個\n'.format(info['name'], num, abs(cancel_num))
        else:
            msg = msg + '尚未點過{}，不可取消\n'.format(info['name'])

    if len(msg) > 0:
        return json_err(msg)

    order_time = datetime.utcnow()
    time = time_translate(order_time)
    order = Order(staff=staff, desk=desk, token=uuid,
                  order_time=order_time, note=note)
    db.session.add(order)

    for p in products:
        product = Product.query.get(p['id'])
        order_product = OrderProduct(quantity=p['num'],
                                     product_name=product.name,
                                     product_price=p['price'])
        order_product.product = product
        order_product.order = order
        db.session.add(order_product)
        db.session.commit()
     
    order = Order.query.filter_by(staff=staff, desk=desk, token=uuid).first()
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    tasks = []
    for pos in POS.query.filter(and_(POS.ip != '', POS.id != 1)).all():

        data = []
        for p in products:
            product = Product.query.get(p['id'])
            if product in pos.products:
                quantity = p['num']
                data.append([product.name, product.price, quantity])
        if len(data) > 0:
            _format = print_order_format(uuid, time, desk.name, staff.name,
                                   pos.split, note, data)
            tasks.append(loop.create_task(send_req(order, pos, _format)))

    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        return json_err(str(e))
    finally:
        config.order_pos_working = POS.order_pos_all_working()
        save_printer_status(dict(order_pos_working=POS.order_pos_all_working(),
            checkout_pos_working=config.checkout_pos_working))
        if config.order_pos_working is False:
            msg = ""
            for pos in POS.query.filter(and_(POS.ip != '', POS.id != 1, POS.error != "")).all():
                msg = msg + 'POS機 id:{} ip:{} \n錯誤:{}'.format(pos.id, pos.ip, pos.error)
            return {'state': 'printer error', 'reason': msg}

        loop.close()
    
    return {'state': 'ok'}


async def send_req(order, pos, data):
    ip = pos.ip
    url = 'http://' + ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=30000'
    headers = {'Content-Type': 'text/xml; charset=utf-8',
               'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
               'SOAPAction': '""'}
    f = partial(requests.post, url, data=data.encode(), headers=headers)
    loop = asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, f)
        if res.status_code is 200:
            tree = ET.fromstring(res.content)
            success = tree[0][0].get('success')
            if success is not 'false':
                status = tree[0][0].get('status')
                if not int(status) & 2:
                    pos.error = pos_error(status)
                    fail = PrintFailed()
                    fail.order = order
                    fail.pos = pos
                    db.session.add(fail)
                else:
                    pos.error = ""
            db.session.commit()
    except (Exception, OSError) as e:
        pos.error = str(e)
        db.session.commit()



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
            details.append((op.product_name, op.product_price, op.quantity, op.price))

    return {'details': details}
