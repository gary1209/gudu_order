from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from werkzeug.security import check_password_hash

from config import config
from models import Staff
from utils import login_required, su_required, flask_login, json_err


app = Blueprint('account', __name__)
db = config.db


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    _next = request.args.get('next')
    name = request.form['username']
    pwd = request.form['password']
    staff = Staff.query.filter_by(name=name).first()
    if not staff:
        return(render_template('login.html', error='帳號或密碼錯誤'))

    if check_password_hash(staff.password, pwd):
        flask_login(staff)
    else:
        return(render_template('login.html', error='帳號或密碼錯誤'))

    if staff.suspended:
        return(render_template('login.html', error='已被停用，請找管理員'))
    if _next:
        return redirect(_next)
    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return 'ok'


@app.route('/list_page', methods=['GET'])
def list_page():
    staffs = Staff.query.order_by(Staff.suspended, Staff.id).all()
    return render_template('account_list.html', staffs=staffs)


@app.route('/register', methods=['POST'])
@login_required
@su_required
def register(staff):
    name = request.form['name']
    pwd = request.form['password']
    pwd_conf = request.form['password_conf']

    if not (name and pwd and pwd_conf):
        return json_err('欄位有空')
    if pwd != pwd_conf:
        return json_err('確認密碼不符')

    staff = Staff.query.filter_by(name=name, suspended=False).first()
    if staff:
        return json_err('名字重複')
    try:
        hashed_pwd = generate_password_hash(pwd)
        staff = Staff(name=name, password=hashed_pwd)
        db.session.add(staff)
        db.session.commit()
    except Exception as e:
        return json_err(str(e))
    else:
        return {'state': 'ok'}


@app.route('/save', methods=['POST'])
@login_required
@su_required
def save(staff):
    staffs = request.json['data']

    for s in staffs:
        _staff = Staff.query.get(s['id'])
        for data in s['data']:
            setattr(_staff, data, s['data'][data])
    db.session.commit()
    return {'state': 'ok'}