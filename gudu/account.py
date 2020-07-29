from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
from werkzeug.security import check_password_hash

from config import config
from models import Staff
from utils import login_required, flask_login, json_err


app = Blueprint('account', __name__)
db = config.db

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    _next = request.args.get('next')
    name = request.form['username']
    pwd = request.form['password']
    staff = Staff.query.filter_by(s_name=name).first()
    if not staff:
        return json_err('user not exist')

    if check_password_hash(staff.password, pwd):
        flask_login(staff)
    else:
        return json_err('password wrong')

    if _next:
        return redirect(_next)
    else:
        return redirect(url_for('index'))