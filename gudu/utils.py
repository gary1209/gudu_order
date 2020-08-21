from functools import wraps

from flask import session, request, redirect, url_for, abort, jsonify
from datetime import datetime, timezone, timedelta

from models import Staff


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


class PrinterError(Exception):
    pass


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
