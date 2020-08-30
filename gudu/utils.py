from functools import wraps

from flask import session, request, redirect, url_for, abort, jsonify
from datetime import datetime, timezone, timedelta

from models import Staff
from config import config

import yaml

def login_required(f):
    '''
    Ref: http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/#login-required-decorator

    the decorated function will be passed a kwarg: ``staff``, an instance of
    models.Staff
    '''
    @wraps(f)
    def wrapper(*args, **kwargs):
        s_id = session.get('s_id')
        if s_id is None:
            return redirect(url_for('account.login_page', next=request.path))

        staff = Staff.query.get(s_id)
        if staff.suspended:
            return redirect(url_for('account.login_page', next=request.path))
        return f(*args, staff=staff, **kwargs)
    return wrapper


def su_required(f):
    @wraps(f)
    def wrapper(*args, staff, **kwargs):
        if not staff.is_su:
            abort(403)
        return f(*args, staff=staff, **kwargs)
    return wrapper


def json_err(reason: str, **others):
    x = {'state': 'error', 'reason': reason}
    x.update(others)
    return jsonify(x)


def flask_login(staff):
    # update http session
    session['s_id'] = staff.id
    return staff


def time_translate(dt):
    dt = dt.replace(tzinfo=timezone.utc)
    tz_utc8 = timezone(timedelta(hours=8))
    local_dt = dt.astimezone(tz_utc8)
    time = local_dt.strftime("%Y/%m/%d %H:%M:%S")
    return time


mapping = {
    0x00000001: 'No printer response\n',
    0x00000004: 'Status of the drawer kick number 3 connector pin = "H"\n',
    0x00000008: 'Offline status\n',
    0x00000020: 'Cover is open\n',
    0x00000040: 'Paper feed switch is feeding paper\n',
    0x00000100: 'Waiting for online recovery\n',
    0x00000200: 'Panel switch is ON\n',
    0x00000400: 'Mechanical error generated\n',
    0x00000800: 'Auto cutter error generated\n',
    0x00002000: 'Unrecoverable error generated\n',
    0x00004000: 'Auto recovery error generated\n',
    0x00020000: '請換紙\n',
    0x00080000: '請換紙\n',
    0x80000000: 'Stop the spooler\n'
}


def pos_error(status):
    msg = ''
    for i in mapping:
        if i & int(status):
            msg = msg + mapping[i]
    return msg


def save_printer_status(data):
    with open('status.yaml', 'w') as f:
        yaml.dump(data, f)


def print_order_format(uuid, time, d_name, s_name, split, note, data, reprint=False):
    name_field_len = 12
    name_len_max = 6
    price_field_len = 7
    total_price_field_len = 8

    reprint_hint = '《補印》&#10;' if reprint else ''

    msg = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
<s:Body>\
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
<text lang="zh-hant"/>'
    if split:
        for info in data:
            p_name = info[0]
            num = info[2]
            if num < 0:
                p_name = '（取消）' + p_name
            msg = msg + '<text width="2" height="2"/>\
<text>{}</text>\
<feed unit="24"/>\
<text>桌號：{}&#10;</text>\
<feed unit="24"/>\
<text>{}x{}&#10;</text>\
<feed unit="24"/>\
<text>備註：{}&#10;</text>\
<cut/>'.format(reprint_hint, d_name, p_name.ljust(name_field_len), abs(num), note)

    else:
        msg = msg + '<text width="2" height="2"/>\
<text>{}</text>\
<text>桌號：{}&#10;</text>\
<text width="1" height="1"/>\
<feed unit="24"/>\
<text>時間：{}&#10;訂單編號：{}&#10;</text>\
<text>開單人員：{}&#10;</text>\
<text>---------------------------------------------&#10;</text>\
<text width="1" height="2"/>\
'.format(reprint_hint, d_name, time, uuid, s_name)

        total_quantity = 0
        order_price = 0
        for info in data:
            p_name = info[0]
            num = info[2]
            price = str(info[1]).rjust(price_field_len)
            total_price = info[1] * num
            total_quantity = total_quantity + num
            order_price = order_price + total_price

            if num < 0:
                p_name = '取消一'+p_name

            if len(p_name) > name_len_max:
                msg = msg + '<text>{name_pre}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
<text>{name_post}&#10;</text>\
'.format(name_pre=p_name[:name_len_max], space='  '*6, num=num,
         price=price, total=str(total_price).rjust(total_price_field_len), name_post=p_name[name_len_max:])

            else:
                msg = msg + '<text>{name}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
'.format(name=p_name, space='  '*(name_field_len-len(p_name)), num=num, price=price,
         total=str(total_price).rjust(total_price_field_len))

        msg = msg + '<text width="1" height="1"/>\
<text>---------------------------------------------&#10;</text>\
<text width="2" height="2"/>\
<text>備註：{}&#10;</text>\
<feed unit="24"/>\
<text>&lt;共{}份&gt;&#10;</text>\
<feed unit="24"/>\
<text>小計：{}&#10;</text>\
<cut/>'.format(note, total_quantity, order_price)

    msg = msg + '</epos-print>\
            </s:Body>\
        </s:Envelope>'
    return msg


def print_bill_format(uuid, time, d_name, s_name, checkout_info, check_price, reprint=False):
    name_field_len = 12
    name_len_max = 6
    price_field_len = 7
    total_price_field_len = 8
    reprint_hint = '《補印》&#10;' if reprint else ''

    msg = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">\
<s:Body>\
<epos-print xmlns="http://www.epson-pos.com/schemas/2011/03/epos-print">\
<text lang="zh-hant"/>\
<text width="2" height="2"/>\
<text>{}</text>\
<feed unit="24"/>\
<text>桌號：{}&#10;</text>\
<text width="1" height="1"/>\
<feed unit="24"/>\
<text>時間：{}&#10;訂單編號：{}&#10;</text>\
<text>結帳人員：{}&#10;</text>\
<text>=============================================&#10;</text>\
<text width="1" height="2"/>\
'.format(reprint_hint, d_name, time, uuid, s_name)


    total_quantity = 0
    for idx, order_products in enumerate(checkout_info):
        if idx is not 0:
            msg = msg + '<text width="1" height="1"/>\
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
                msg = msg + '<text>{name_pre}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
<text>{name_post}&#10;</text>\
'.format(name_pre=p_name[:name_len_max], space='  '*6, num=num,
         price=price, total=str(op.price).rjust(total_price_field_len), name_post=p_name[name_len_max:])

            else:
                msg = msg + '<text>{name}</text>\
<text>{space}x {num}{price}{total}&#10;</text>\
'.format(name=p_name, space='  '*(name_field_len-len(p_name)), num=num, price=price,
         total=str(op.price).rjust(total_price_field_len))

    msg = msg + '<text width="1" height="1"/>\
<text>=============================================&#10;</text>\
<text width="2" height="2"/>\
<text>&lt;共{}份&gt;&#10;</text>\
<feed unit="24"/>\
<text>合計：{}&#10;</text><cut/>\
</epos-print>\
</s:Body>\
</s:Envelope>'.format(total_quantity, check_price)
    return msg
