import sqlite3

connection = sqlite3.connect("nexora.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

connection.commit()
connection.close()
# Create courses and enrollments tables

connection = sqlite3.connect("nexora.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    credits INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    progress INTEGER DEFAULT 0,
    attendance INTEGER DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")
# Add progress and attendance to existing enrollments table
try:
    cursor.execute("ALTER TABLE enrollments ADD COLUMN progress INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE enrollments ADD COLUMN attendance INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS support_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    message TEXT,
    category TEXT,
    priority TEXT,
    department TEXT,
    status TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    day TEXT,
    start_time TEXT,
    end_time TEXT,
    room TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")
connection.commit()
connection.close()