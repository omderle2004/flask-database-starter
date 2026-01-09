"""
Part 5: PostgreSQL/MySQL with Environment Configuration
========================================================
Switch from SQLite to production-ready databases!

What You'll Learn:
- Connecting to PostgreSQL and MySQL
- Environment variables for configuration
- python-dotenv for .env files
- Database URL formats
- Connection pooling basics

Prerequisites: Complete all previous parts
Install: pip install psycopg2-binary pymysql python-dotenv
"""
import time

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv  # Load .env file

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Get from env or use fallback

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Get database URL from environment variable
# Falls back to SQLite if not set
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool settings (for production)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,  # Number of connections to keep open
    'pool_recycle': 3600,  # Recycle connections after 1 hour
    'pool_pre_ping': True,  # Check connection validity before using
}

db = SQLAlchemy(app)


# =============================================================================
# MODEL
# =============================================================================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Product {self.name}>'


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    products = Product.query.all()
    # Show which database is being used
    db_type = 'Unknown'
    db_url = DATABASE_URL.lower()
    if 'postgresql' in db_url or 'postgres' in db_url:
        db_type = 'PostgreSQL'
    elif 'mysql' in db_url:
        db_type = 'MySQL'
    elif 'sqlite' in db_url:
        db_type = 'SQLite'

    return render_template('index.html', products=products, db_type=db_type, db_url=DATABASE_URL)


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        new_product = Product(
            name=request.form['name'],
            price=float(request.form['price']),
            stock=int(request.form.get('stock', 0)),
            description=request.form.get('description', '')
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'danger')
    return redirect(url_for('index'))

@app.route('/performance-test')
def performance_test():
    start = time.time()
    products = Product.query.all()
    end = time.time()

    return {
        "database": DATABASE_URL,
        "records": len(products),
        "time_taken_seconds": round(end - start, 6)
    }


# =============================================================================
# INITIALIZE DATABASE
# =============================================================================

from sqlalchemy.exc import OperationalError

def init_db():
    try:
        with app.app_context():
            db.create_all()
            print(f"✅ Connected to DB: {DATABASE_URL}")

            if Product.query.count() == 0:
                sample = [
                    Product(name='Laptop', price=999.99, stock=10),
                    Product(name='Mouse', price=29.99, stock=50),
                ]
                db.session.add_all(sample)
                db.session.commit()
                print("📦 Sample data added")

    except OperationalError as e:
        print("❌ Database connection failed")
        print("Reason:", e)


if __name__ == '__main__':
    init_db()
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')


# =============================================================================
# DATABASE URL FORMATS:
# =============================================================================
#
# SQLite (File-based, no server needed):
#   sqlite:///database.db
#   sqlite:///path/to/database.db
#
# PostgreSQL:
#   postgresql://username:password@host:port/database_name
#   postgresql://postgres:mypassword@localhost:5432/mydb
#
# MySQL:
#   mysql+pymysql://username:password@host:port/database_name
#   mysql+pymysql://root:mypassword@localhost:3306/mydb
#
# =============================================================================
# SETTING UP POSTGRESQL:
# =============================================================================
#
# 1. Install PostgreSQL
# 2. Create a database:
#    psql -U postgres
#    CREATE DATABASE flask_demo;
#
# 3. Set environment variable:
#    DATABASE_URL=postgresql://postgres:password@localhost:5432/flask_demo
#
# 4. Install Python driver:
#    pip install psycopg2-binary
#
# =============================================================================
# SETTING UP MYSQL:
# =============================================================================
#
# 1. Install MySQL
# 2. Create a database:
#    mysql -u root -p
#    CREATE DATABASE flask_demo;
#
# 3. Set environment variable:
#    DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flask_demo
#
# 4. Install Python driver:
#    pip install pymysql
#
# =============================================================================
# ENVIRONMENT VARIABLES:
# =============================================================================
#
# Option 1: Set in terminal
#   Windows: set DATABASE_URL=postgresql://...
#   Linux/Mac: export DATABASE_URL=postgresql://...
#
# Option 2: Use .env file (recommended)
#   Create .env file with:
#     DATABASE_URL=postgresql://...
#     SECRET_KEY=your-secret-key
#
#   Then load with python-dotenv (already done in this file)
#
# =============================================================================
