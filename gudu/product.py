from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, jsonify, abort
import operator

from config import config
from models import Product, Category, OrderProduct, POS, PosProduct
from utils import login_required, su_required, json_err

app = Blueprint('product', __name__)
db = config.db


@app.route('/', methods=['GET'], strict_slashes=False)
@login_required
@su_required
def mgmt_page(staff):
    categories = Category.query.order_by(Category.id).all()
    _cate = []
    for c in categories:
        _cate.append((c, c.products))
    return render_template('product_mgmt.html', categories=categories,
        info=_cate, staff=staff)


@app.route('/category', methods=['POST'], strict_slashes=False)
@login_required
@su_required
def add_category(staff):
    name = request.json['name']
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return 'ok'


@app.route('/<int:p_id>', methods=['GET'], strict_slashes=False)
@login_required
@su_required
def product_info(p_id, staff):
    product = Product.query.get(p_id)
    if not product:
        abort(403)
    categories = Category.query.order_by(Category.id).all()
    poss = list(map(lambda x: x.id, product.poss))
    return render_template('product.html', product=product,
                           categories=categories, poss=poss, staff=staff)


@app.route('/<int:p_id>', methods=['POST'], strict_slashes=False)
@login_required
@su_required
def save_product(p_id, staff):
    for f in ('p_name', 'price', 'c_id', 'pos_machs', 'available'):
        if f not in request.json:
            return json_err('field `{}` is required'.format(f)), 400

    p_name = request.json['p_name']
    price = request.json['price']
    c_id = request.json['c_id']
    pos_machs = request.json['pos_machs']
    available = request.json['available']

    if p_id != 0:
        product = Product.query.get(p_id)
        if not product:
            abort(403)
        category = Category.query.get(c_id)
        if not category:
            abort(403)
        product.name = p_name
        product.price = price
        product.category = category
        product.available = available
        db.session.commit()

        for pp in product.pos_products:
            if pp.pos.id not in pos_machs:
                db.session.delete(pp)
                db.session.commit()

        for id in pos_machs:
            pos = POS.query.get(id)
            if pos not in product.poss:
                pos_product = PosProduct()
                pos_product.pos = pos
                pos_product.product = product
                db.session.add(pos_product)
        db.session.commit()

    else:
        category = Category.query.get(c_id)
        if not category:
            abort(403)
        product = Product(name=p_name, price=price, available=available)
        product.category = category
        db.session.add(product)
        db.session.commit()
        for id in pos_machs:
            pos = POS.query.get(id)
            pos_product = PosProduct()
            pos_product.pos = pos
            pos_product.product = product
            db.session.add(pos_product)
        db.session.commit()

    return {'state': 'ok', 'category': c_id}


@app.route('/create/<int:c_id>', methods=['GET'], strict_slashes=False)
@login_required
@su_required
def create_product_page(c_id, staff):
    # categories = Category.query.all()
    category = Category.query.get(c_id)
    return render_template('product.html', product={'pos_machs': [1]}, 
        selected_category=category, staff=staff)
