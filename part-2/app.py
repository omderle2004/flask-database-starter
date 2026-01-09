from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

DATABASE = 'students.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# ---------------- CREATE ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()

        # EMAIL VALIDATION
        existing = conn.execute(
            'SELECT * FROM students WHERE email = ?',
            (email,)
        ).fetchone()

        if existing:
            flash('Email already exists!', 'danger')
            conn.close()
            return redirect(url_for('add_student'))

        conn.execute(
            'INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
            (name, email, course)
        )
        conn.commit()
        conn.close()

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


# ---------------- READ + SEARCH ----------------
@app.route('/')
def index():
    search = request.args.get('q')

    conn = get_db_connection()
    if search:
        students = conn.execute(
            'SELECT * FROM students WHERE name LIKE ?',
            ('%' + search + '%',)
        ).fetchall()
    else:
        students = conn.execute(
            'SELECT * FROM students ORDER BY id DESC'
        ).fetchall()

    conn.close()
    return render_template('index.html', students=students)


# ---------------- UPDATE ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn.execute(
            'UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?',
            (name, email, course, id)
        )
        conn.commit()
        conn.close()

        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()
    conn.close()

    return render_template('edit.html', student=student)


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
