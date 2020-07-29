from functools import wraps

from flask import session, request, redirect, url_for, abort, jsonify

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
            return redirect(url_for('account.login', next=request.path))

        staff = Staff.query.get(s_id)
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
    session['s_id'] = staff.s_id
    return staff

