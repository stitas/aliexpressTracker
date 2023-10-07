from flask import Flask, request, render_template, flash, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from scrape import get_product_data
from dotenv import load_dotenv
import datetime
import os

load_dotenv('.env')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(1000))
    discounted_price = db.Column(db.Float)
    original_price = db.Column(db.Float)
    rating = db.Column(db.Float)
    img = db.Column(db.String(1000))
    currency = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self,title,url,discounted_price,original_price,rating,img,currency):
        self.title = title
        self.url = url
        self.discounted_price = discounted_price
        self.original_price = original_price
        self.rating = rating
        self.img = img
        self.currency = currency
        
class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    price = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self,product_id,price):
        self.product_id = product_id
        self.price = price
        
        
@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if 'search' in request.form:
            url = request.form['product_url']
            return redirect(url_for('search_product',url=url))
        if 'go_to_list' in request.form:
            return redirect(url_for('show_all_products'))
    return render_template('index.html')

@app.route('/search-product', methods=['POST','GET'])
def search_product():
    url = request.args['url']
    data = get_product_data(url)
    if request.method == 'POST':
        if 'add_to_db' in request.form:
            exists = db.session.query(db.session.query(Product).filter_by(url=data['url']).exists()).scalar()
            if not exists:
                product = Product(data['title'],data['url'],data['discountedPrice'],data['originalPrice'],data['rating'],data['image'],data['currency'])
                db.session.add(product)
                product = Product.query.filter_by(url=data['url']).first()
                if data['discountedPrice']:
                    price = PriceHistory(product.id,data['discountedPrice'])
                else:
                    price = PriceHistory(product.id,data['originalPrice'])
                db.session.add(price)
                db.session.commit()
                flash('Product has been added to the list')
            else:
                flash('Product already exists')
    return render_template('product.html',data=data)

@app.route('/show-all-products')
def show_all_products():
    data = Product.query.all()
    return render_template('all_products.html',data=data)

@app.route('/product/<id>', methods=['POST','GET'])
def product_detail(id):
    product = Product.query.filter_by(id=id).first()
    price_history = PriceHistory.query.filter_by(product_id=product.id).all()
    if 'delete_btn' in request.form:
        db.session.query(Product).filter_by(id=id).delete()
        db.session.commit()
        return redirect(url_for('show_all_products'))
    return render_template('product_detail.html',product=product, price_history=price_history)

@app.route('/update-price-history', methods=['POST'])   
def update_price_history():
    products = Product.query.all()
    for product in products:
        url = product.url
        data = get_product_data(url)
        if data != {}:
            if data['discountedPrice']:
                price = PriceHistory(product.id, data['discountedPrice'])
                product.discounted_price = data['discountedPrice'] 
            else: 
                price = PriceHistory(product.id, data['originalPrice'])
                product.original_price = data['originalPrice']
            product.rating = data['rating']
            product.last_updated = datetime.datetime.utcnow()
        else:
            response = {'message' : 'No data on product'}
        db.session.add(price)
        db.session.commit() 
        
    response = {'message' : 'Updated price history'}    
    return jsonify(response)
      
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        db.session.commit()
    app.run(debug=True)
