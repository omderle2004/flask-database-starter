from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODEL ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

# ---------------- ROUTES ----------------

# HOME + SEARCH + DASHBOARD
@app.route('/')
def index():
    search = request.args.get('search')

    if search:
        products = Product.query.filter(
            Product.name.ilike(f"%{search}%")
        ).all()
    else:
        products = Product.query.all()

    total_products = Product.query.count()
    total_value = db.session.query(
        func.sum(Product.quantity * Product.price)
    ).scalar() or 0

    return render_template(
        'index.html',
        products=products,
        total_products=total_products,
        total_value=round(total_value, 2)
    )

# ADD PRODUCT
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            quantity=int(request.form['quantity']),
            price=float(request.form['price'])
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

# EDIT PRODUCT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', product=product)

# DELETE PRODUCT
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

# ---------------- RUN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
S