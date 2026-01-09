"""
Part 3: Flask-SQLAlchemy ORM
============================
Say goodbye to raw SQL! Use Python classes to work with databases.

What You'll Learn:
- Setting up Flask-SQLAlchemy
- Creating Models (Python classes = database tables)
- ORM queries instead of raw SQL
- Relationships between tables (One-to-Many)

Prerequisites: Complete part-1 and part-2
Install: pip install flask-sqlalchemy
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  # Database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warning

db = SQLAlchemy(app)  # Initialize SQLAlchemy with app


# =============================================================================
# MODELS (Python Classes = Database Tables)
# =============================================================================

# =============================================================================
# MODELS
# =============================================================================

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # One teacher -> many courses
    courses = db.relationship('Course', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.name}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Foreign key to Teacher
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    # One course -> many students
    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# =============================================================================
# ROUTES - Using ORM instead of raw SQL
# =============================================================================

@app.route('/')
def index():
    # OLD WAY (raw SQL): conn.execute('SELECT * FROM students').fetchall()
    # NEW WAY (ORM):
    students = Student.query.all()  # Get all students
    return render_template('index.html', students=students)


@app.route('/courses')
def courses():
    all_courses = Course.query.all()  # Get all courses
    return render_template('courses.html', courses=all_courses)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        # OLD WAY: conn.execute('INSERT INTO students...')
        # NEW WAY:
        new_student = Student(name=name, email=email, course_id=course_id)  # Create object
        db.session.add(new_student)  # Add to session
        db.session.commit()  # Save to database

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()  # Get courses for dropdown
    return render_template('add.html', courses=courses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
    # NEW WAY:
    student = Student.query.get_or_404(id)  # Get by ID or show 404 error

    if request.method == 'POST':
        student.name = request.form['name']  # Just update the object
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()  # Save changes
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)  # Delete the object
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')  # Optional field

        new_course = Course(name=name, description=description)
        db.session.add(new_course)
        db.session.commit()

        flash('Course added!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html')

@app.route('/queries-demo')
def queries_demo():
    return {
        "filter": [s.name for s in Student.query.filter(Student.name.like('%a%')).all()],
        "order_by": [s.name for s in Student.query.order_by(Student.name).all()],
        "limit": [s.name for s in Student.query.limit(2).all()]
    }

@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)

# =============================================================================
# CREATE TABLES AND ADD SAMPLE DATA
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()

        if Teacher.query.count() == 0:
            teachers = [
                Teacher(name='Mr. Sharma', email='sharma@school.com'),
                Teacher(name='Ms. Patil', email='patil@school.com'),
            ]
            db.session.add_all(teachers)
            db.session.commit()

        if Course.query.count() == 0:
            courses = [
                Course(
                    name='Python Basics',
                    description='Learn Python fundamentals',
                    teacher_id=1
                ),
                Course(
                    name='Web Development',
                    description='HTML, CSS, Flask',
                    teacher_id=2
                ),
                Course(
                    name='Data Science',
                    description='Data analysis with Python',
                    teacher_id=1
                )
            ]
            db.session.add_all(courses)
            db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# ORM vs RAW SQL COMPARISON:
# =============================================================================
#
# Operation      | Raw SQL                          | SQLAlchemy ORM
# ---------------|----------------------------------|---------------------------
# Get all        | SELECT * FROM students           | Student.query.all()
# Get by ID      | SELECT * WHERE id = ?            | Student.query.get(id)
# Filter         | SELECT * WHERE name = ?          | Student.query.filter_by(name='John')
# Insert         | INSERT INTO students VALUES...   | db.session.add(student)
# Update         | UPDATE students SET...           | student.name = 'New'; db.session.commit()
# Delete         | DELETE FROM students WHERE...    | db.session.delete(student)
#
# =============================================================================
# COMMON QUERY METHODS:
# =============================================================================
#
# Student.query.all()                    - Get all records
# Student.query.first()                  - Get first record
# Student.query.get(1)                   - Get by primary key
# Student.query.get_or_404(1)            - Get or show 404 error
# Student.query.filter_by(name='John')   - Filter by exact value
# Student.query.filter(Student.name.like('%john%'))  - Filter with LIKE
# Student.query.order_by(Student.name)   - Order results
# Student.query.count()                  - Count records
#
# =============================================================================
