from flask import Flask, render_template
from config import config

from account import app as account_app
from order import app as order_app
from product import app as product_app
from utils import login_required, su_required
from models import Desk, POS

app = Flask(__name__)
app.register_blueprint(account_app, url_prefix='/account')
app.register_blueprint(order_app, url_prefix='/order')
app.register_blueprint(product_app, url_prefix='/product')

@app.route('/')
@login_required
def index(staff):
    '''
        regular: hopmepage > order
        su: homepage > order, staff mgmt, prod mgmt, desk mgmt
        all: logout in navbar
    '''
    return render_template('homepage.html', staff=staff)


@app.route('/pos')
@login_required
@su_required
def pos_page(staff):
    pos_machs = POS.query.all()
    return render_template('pos.html', pos_machs=pos_machs)

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
