from flask import Flask, render_template, request, url_for, redirect
from config import config

import asyncio
import requests
from functools import partial
import xml.etree.ElementTree as ET

from account import app as account_app
from order import app as order_app
from checkout import app as checkout_app
from product import app as product_app
from utils import login_required, su_required, time_translate
from utils import pos_error, save_printer_status, print_order_format, print_bill_format
from models import Desk, POS, PrintFailed, Checkout, Order

app = Flask(__name__)
app.register_blueprint(account_app, url_prefix='/account')
app.register_blueprint(order_app, url_prefix='/order')
app.register_blueprint(product_app, url_prefix='/product')
app.register_blueprint(checkout_app, url_prefix='/checkout')

db = config.db


@app.route('/')
@login_required
def index(staff):
    return render_template('homepage.html', staff=staff)


@app.route('/desks')
@login_required
def desk_page(staff):
    desks = {}
    prefix = ['0', '1', '2', '3', '5', '6', '外']
    for p in prefix:
        d = Desk.query.filter(Desk.name.startswith(p)).all()
        desks[p] = d
    return render_template('desk.html', desks=desks, staff=staff)


@app.route('/desk/sit/<int:id>', methods=['POST'])
@login_required
def sit(id, staff):
    desk = Desk.query.get(id)
    if not desk:
        abort(403)
    desk.occupied = True
    db.session.commit()
    return {'state': 'ok'}


@app.route('/desk/leave/<int:id>', methods=['POST'])
@login_required
def leave(id, staff):
    desk = Desk.query.get(id)
    if not desk:
        abort(403)
    desk.occupied = False
    db.session.commit()
    return {'state': 'ok'}


@app.route('/pos')
@login_required
@su_required
def pos_page(staff):
    pos_machs = POS.query.all()
    return render_template('pos.html', pos_machs=pos_machs, staff=staff)


@app.route('/pos', methods=['POST'])
@login_required
@su_required
def save_pos(staff):
    pos_machs = request.json['data']

    for pos in pos_machs:
        p = POS.query.get(pos['pos_id'])
        p.ip = pos['ip']
        p.name = pos['pos_name']
        p.split = pos['split']
    db.session.commit()
    return {'state': 'ok'}


@app.route('/pos/fix')
@login_required
def error_page(staff):
    pos_machs = POS.query.filter(POS.error != "").all()
    return render_template('pos_error.html', pos=pos_machs, staff=staff)


@app.route('/pos/fix', methods=['POST'])
@login_required
def fix_pos_error(staff):
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    tasks = []
    # send empty requests to test pos machines
    for pos in POS.query.filter(POS.ip != '').all():
        tasks.append(loop.create_task(send_req(pos)))

    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        config.order_pos_working = POS.order_pos_all_working()
        save_printer_status({'order_pos_working': config.order_pos_working,
            'checkout_pos_working': config.checkout_pos_working
        })
        if config.order_pos_working is False:
            return {'state': 'error'}
        else:
            tasks = []
            # reprint orders
            for pos in POS.query.filter(POS.ip != '').all():
                for print_failed in pos.fails:
                    order = print_failed.order
                    uuid = order.token
                    time = time_translate(order.order_time)
                    desk_name = Desk.query.get(order.desk_id).name
                    staff_name = order.staff.name
                    note = order.note
                    data = []
                    for op in order.order_products:
                        quantity = op.quantity
                        data.append([op.product_name, op.product_price, quantity])
                    _format = print_order_format(uuid, time, desk_name, staff_name,
                                   pos.split, note, data, reprint=True)
                    tasks.append(loop.create_task(send_req(pos, _format, order)))
            # reprint checkout
            pos = POS.query.get(1)
            for c in Checkout.query.filter_by(printed=False).all():
                uuid = c.token
                time = time_translate(c.checkout_time)
                d_name = c.desk_name
                s_name = c.staff.name
                check_price = c.total_price
                checkout_info = []
                for order in Order.query.filter_by(token=uuid).all():
                    checkout_info.append(order.order_products)
                _format = print_bill_format(uuid, time, d_name, s_name, checkout_info, check_price, reprint=True)
                tasks.append(loop.create_task(send_req(pos, _format, checkout=c)))
            try:
                loop.run_until_complete(asyncio.gather(*tasks))
            finally:
                config.order_pos_working = POS.order_pos_all_working()
                config.checkout_pos_working = Checkout.all_printed()
                save_printer_status({'order_pos_working': POS.order_pos_all_working(),
                    'checkout_pos_working': Checkout.all_printed()
                })
            if config.order_pos_working or config.checkout_pos_working is False:
                return {'state': 'error'}

        loop.close()

    return {'state': 'ok'}


async def send_req(pos, data=None, order=None, checkout=None):
    ip = pos.ip
    url = 'http://' + ip + '/cgi-bin/epos/service.cgi?devid=local_printer&timeout=30000'
    headers = {'Content-Type': 'text/xml; charset=utf-8',
               'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
               'SOAPAction': '""'}
    if not data:
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
<s:Body>\
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print"></epos-print>\
</s:Body>\
</s:Envelope>'
    f = partial(requests.post, url, data=data.encode(), headers=headers)
    loop = asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, f)
    except (Exception, OSError) as e:
        pos.error = str(e)
        db.session.commit()

    if res.status_code is 200:
        tree = ET.fromstring(res.content)
        success = tree[0][0].get('success')
        if success is not 'false':
            status = tree[0][0].get('status')
            if not int(status) & 2:
                pos.error = pos_error(status)
            else:
                if order:
                    print_failed = PrintFailed.query.filter_by(pos=pos, order=order).first()
                    db.session.delete(print_failed)
                    db.session.commit()
                if checkout:
                    checkout.printed = True
                    db.session.commit()
                pos.error = ""
        db.session.commit()


@app.template_filter('hide_null')
def null_filter(s):
    return s if not s == None else ''


def setup_db():
    db_url = 'sqlite:///../db/gudu.db'

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config.app = app  # this will initialize the db connection
    import models  # import the model declaration
    config.db.create_all(app=app)


def main():
    setup_db()
    # [TODO] move secret key to config file
    app.config['SECRET_KEY'] = 'hu'
    app.run(
        host=config.host,
        port=config.port,
        threaded=True,
        debug=config.debug,
    )


if __name__ == '__main__':
    main()
