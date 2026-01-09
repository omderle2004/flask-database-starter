"""
Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You'll Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =============================================================================
# MODELS
# =============================================================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):  # Convert model to dictionary for JSON response
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'isbn': self.isbn,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# =============================================================================
# REST API ROUTES
# =============================================================================

@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    query = Book.query

    # Sorting
    if hasattr(Book, sort):
        column = getattr(Book, sort)
        if order == 'desc':
            column = column.desc()
        query = query.order_by(column)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'books': [book.to_dict() for book in pagination.items]
    })


# POST /api/books - Create new book
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()  # Get JSON data from request body

    # Validation
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title') or not data.get('author'):
        return jsonify({'success': False, 'error': 'Title and author are required'}), 400

    # Check for duplicate ISBN
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    # Create book
    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data.get('year'),  # Optional field
        isbn=data.get('isbn')
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201  # 201 = Created


# PUT /api/books/<id> - Update book
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.to_dict()
    })


# DELETE /api/books/<id> - Delete book
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })


# =============================================================================
# BONUS: Search and Filter
# =============================================================================

# GET /api/books/search?q=python&author=john
@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query

    # Filter by title (partial match)
    title = request.args.get('q')  # Query parameter: ?q=python
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))  # Case-insensitive LIKE

    # Filter by author
    author = request.args.get('author')
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    # Filter by year
    year = request.args.get('year')
    if year:
        query = query.filter_by(year=int(year))

    books = query.all()

    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })


# =============================================================================
# SIMPLE WEB PAGE FOR TESTING
# =============================================================================

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Book API Frontend</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f4f6f8; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; border: 1px solid #ddd; }
        th { background: #4CAF50; color: white; cursor: pointer; }
        tr:nth-child(even) { background: #f9f9f9; }
        button { padding: 8px 14px; margin: 10px 5px; }
    </style>
</head>
<body>

<h1>📚 Book Library (Flask REST API)</h1>

<table>
    <thead>
        <tr>
            <th onclick="loadBooks('title')">Title</th>
            <th onclick="loadBooks('author')">Author</th>
            <th onclick="loadBooks('year')">Year</th>
            <th>ISBN</th>
        </tr>
    </thead>
    <tbody id="bookTable"></tbody>
</table>

<div>
    <button onclick="prevPage()">⬅ Prev</button>
    <span id="pageInfo"></span>
    <button onclick="nextPage()">Next ➡</button>
</div>

<script>
let page = 1;
let sort = 'id';
let order = 'asc';

function loadBooks(sortField = null) {
    if (sortField) {
        sort = sortField;
        order = order === 'asc' ? 'desc' : 'asc';
    }

    fetch(`/api/books?page=${page}&per_page=5&sort=${sort}&order=${order}`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('bookTable');
            table.innerHTML = '';

            data.books.forEach(book => {
                table.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.year ?? '-'}</td>
                        <td>${book.isbn ?? '-'}</td>
                    </tr>
                `;
            });

            document.getElementById('pageInfo').innerText =
                `Page ${page} | Total Books: ${data.total}`;
        });
}

function nextPage() {
    page++;
    loadBooks();
}

function prevPage() {
    if (page > 1) {
        page--;
        loadBooks();
    }
}

loadBooks();
</script>

</body>
</html>
'''




# =============================================================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        if Book.query.count() == 0:
            sample_books = [
                Book(title='Python Crash Course', author='Eric Matthes', year=2019, isbn='978-1593279288'),
                Book(title='Flask Web Development', author='Miguel Grinberg', year=2018, isbn='978-1491991732'),
                Book(title='Clean Code', author='Robert C. Martin', year=2008, isbn='978-0132350884'),
            ]
            db.session.add_all(sample_books)
            db.session.commit()
            print('Sample books added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================
