from flask import Flask, render_template, request, url_for, redirect
from config import config

from account import app as account_app
from order import app as order_app
from checkout import app as checkout_app
from product import app as product_app
from utils import login_required, su_required
from models import Desk, POS

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
    prefix = ['1', '2', '3', 'A', '外']
    for p in prefix:
        d = Desk.query.filter(Desk.name.startswith(p)).all()
        desks[p] = d
    return render_template('desk.html', desks=desks)


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
    return render_template('pos.html', pos_machs=pos_machs)


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
