# Part 5: PostgreSQL/MySQL with Environment Configuration

## One-Line Summary
Switching to PostgreSQL/MySQL with environment configuration

## What You'll Learn
- Connecting to PostgreSQL and MySQL
- Environment variables for configuration
- python-dotenv for .env files
- Database URL formats

## Prerequisites
- Complete all previous parts
- Install: `pip install psycopg2-binary pymysql python-dotenv`

## How to Run

### With SQLite (Default):
```bash
cd part-7
pip install python-dotenv
python app.py
```

### With PostgreSQL:
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Create .env file
cp .env.example .env

# Edit .env and set:
DATABASE_URL=postgresql://postgres:password@localhost:5432/flask_demo

# Run app
python app.py
```

### With MySQL:
```bash
# Install MySQL driver
pip install pymysql

# Create .env file
cp .env.example .env

# Edit .env and set:
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/flask_demo

# Run app
python app.py
```

## Database URL Formats

| Database | URL Format |
|----------|------------|
| SQLite | `sqlite:///filename.db` |
| PostgreSQL | `postgresql://user:pass@host:5432/dbname` |
| MySQL | `mysql+pymysql://user:pass@host:3306/dbname` |

## Setting Up PostgreSQL

```bash
# 1. Install PostgreSQL (varies by OS)

# 2. Access PostgreSQL
psql -U postgres

# 3. Create database
CREATE DATABASE flask_demo;

# 4. Exit
\q

# 5. Set DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/flask_demo
```

## Setting Up MySQL

```bash
# 1. Install MySQL (varies by OS)

# 2. Access MySQL
mysql -u root -p

# 3. Create database
CREATE DATABASE flask_demo;

# 4. Exit
exit

# 5. Set DATABASE_URL in .env
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/flask_demo
```

## Environment Variables

### Option 1: .env file (Recommended)
```
# .env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
```

### Option 2: Terminal
```bash
# Windows
set DATABASE_URL=postgresql://...

# Linux/Mac
export DATABASE_URL=postgresql://...
```

## Key Files
```
part-7/
├── app.py              <- Database config with env vars
├── .env.example        <- Example environment file
├── templates/
│   ├── index.html      <- Shows current database type
│   └── add.html
└── README.md
```

## Connection Pool Settings
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,        # Connections to keep open
    'pool_recycle': 3600,   # Recycle after 1 hour
    'pool_pre_ping': True,  # Verify connection before use
}
```

## SQLite vs PostgreSQL vs MySQL

| Feature | SQLite | PostgreSQL | MySQL |
|---------|--------|------------|-------|
| Setup | None | Server needed | Server needed |
| Concurrency | Limited | Excellent | Good |
| Use Case | Development, Small apps | Production | Production |
| Performance | Fast for small data | Excellent | Excellent |

##Exercise
1. Set up PostgreSQL locally and connect your app
2. Compare query performance between SQLite and PostgreSQL
3. Add connection error handling

## Congratulations!
You've completed all 5 parts of Flask Database learning!

### What You Learned:
1. **Part 1:** Basic SQLite connection
2. **Part 2:** Full CRUD operations
3. **Part 3:** SQLAlchemy ORM
4. **Part 4:** REST API
5. **Part 5:** Production databases
