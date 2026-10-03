from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel

app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HOME ----------------

@app.get("/")
def home():
    return {
        "message": "NEXORA AI Student Support System is running!"
    }

# ---------------- STUDENTS ----------------

@app.get("/students")
def get_students():
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    connection.close()

    return {"students": students}


class Student(BaseModel):
    name: str
    email: str
    password: str


@app.post("/students")
def add_student(student: Student):
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO students (name, email, password) VALUES (?, ?, ?)",
        (student.name, student.email, student.password)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Student registered successfully"
    }


# ---------------- LOGIN ----------------

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login_student(data: LoginRequest):
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE email = ? AND password = ?",
        (data.email, data.password)
    )

    student = cursor.fetchone()

    connection.close()

    if student:
        return {
            "message": "Login successful",
            "student": {
                "id": student[0],
                "name": student[1],
                "email": student[2]
            }
        }

    return {
        "message": "Invalid email or password"
    }


# ---------------- COURSES ----------------

class Course(BaseModel):
    name: str
    code: str
    credits: int


@app.post("/courses")
def add_course(course: Course):
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO courses (name, code, credits) VALUES (?, ?, ?)",
        (course.name, course.code, course.credits)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Course added successfully"
    }


# ---------------- ENROLLMENT ----------------

class Enrollment(BaseModel):
    student_id: int
    course_id: int


@app.post("/enroll")
def enroll_student(data: Enrollment):
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
        (data.student_id, data.course_id)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Student enrolled successfully"
    }


@app.get("/students/{student_id}/courses")
def get_student_courses(student_id: int):
    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            courses.id,
            courses.name,
            courses.code,
            courses.credits
        FROM courses
        JOIN enrollments
        ON courses.id = enrollments.course_id
        WHERE enrollments.student_id = ?
    """, (student_id,))

    courses = cursor.fetchall()

    connection.close()

    return {
        "courses": courses
    }


# ---------------- SUPPORT / COMPLAINT ----------------

class SupportRequest(BaseModel):
    student_id: int
    message: str


@app.post("/support")
def create_support_request(data: SupportRequest):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

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

    # ---------------- AI-ASSISTED CLASSIFICATION ----------------

    message = data.message.lower()

    if (
        "payment" in message
        or "paid" in message
        or "fee" in message
        or "refund" in message
        or "transaction" in message
    ):

        category = "Payment"
        priority = "High"
        department = "Accounts"

        suggested_response = (
            "Your payment-related issue has been identified as a high-priority "
            "request. The Accounts department will review your payment and "
            "enrollment details."
        )

    elif (
        "course" in message
        or "class" in message
        or "recording" in message
        or "lecture" in message
        or "video" in message
    ):

        category = "Course"
        priority = "Medium"
        department = "Technical Support"

        suggested_response = (
            "Your course-related issue has been identified. Technical Support "
            "will check your course access, class recording, or learning "
            "resources."
        )

    elif (
        "certificate" in message
        or "certification" in message
    ):

        category = "Certificate"
        priority = "Medium"
        department = "Administration"

        suggested_response = (
            "Your certificate-related request has been received. The "
            "Administration department will verify your eligibility and "
            "certificate status."
        )

    elif (
        "login" in message
        or "password" in message
        or "account" in message
        or "access" in message
    ):

        category = "Account / Technical"
        priority = "High"
        department = "Technical Support"

        suggested_response = (
            "Your account or access issue has been identified as a high-priority "
            "technical request. Technical Support will review your account "
            "access."
        )

    elif (
        "attendance" in message
        or "absent" in message
        or "present" in message
    ):

        category = "Attendance"
        priority = "Medium"
        department = "Academic Support"

        suggested_response = (
            "Your attendance-related request has been received. Academic Support "
            "will verify your attendance records."
        )

    else:

        category = "General"
        priority = "Medium"
        department = "Student Support"

        suggested_response = (
            "Your request has been received and classified as a general "
            "student-support issue. The Student Support team will review it "
            "and assist you."
        )

    # ---------------- SAVE REQUEST ----------------

    cursor.execute("""
        INSERT INTO support_requests
        (
            student_id,
            message,
            category,
            priority,
            department,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.student_id,
        data.message,
        category,
        priority,
        department,
        "Pending"
    ))

    connection.commit()

    request_id = cursor.lastrowid

    connection.close()

    # ---------------- RESPONSE ----------------

    return {
        "message": "Support request created successfully",
        "request_id": request_id,
        "category": category,
        "priority": priority,
        "department": department,
        "status": "Pending",
        "suggested_response": suggested_response
    }


# ---------------- VIEW SUPPORT REQUESTS ----------------

@app.get("/support/{student_id}")
def get_support_requests(student_id: int):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            message,
            category,
            priority,
            department,
            status
        FROM support_requests
        WHERE student_id = ?
    """, (student_id,))

    requests = cursor.fetchall()

    connection.close()

    return {
        "support_requests": requests
    }


# ---------------- ADMIN SUPPORT REQUESTS ----------------

@app.get("/admin/support")
def get_all_support_requests():

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            student_id,
            message,
            category,
            priority,
            department,
            status
        FROM support_requests
    """)

    requests = cursor.fetchall()

    connection.close()

    return {
        "support_requests": requests
    }


# ---------------- STUDENT DASHBOARD ----------------

@app.get("/students/{student_id}/dashboard")
def get_student_dashboard(student_id: int):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    # Student information
    cursor.execute("""
        SELECT
            id,
            name,
            email
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        connection.close()

        return {
            "message": "Student not found"
        }

    # Courses
    cursor.execute("""
        SELECT
            courses.id,
            courses.name,
            courses.code,
            courses.credits,
            enrollments.progress,
            enrollments.attendance
        FROM courses
        JOIN enrollments
        ON courses.id = enrollments.course_id
        WHERE enrollments.student_id = ?
    """, (student_id,))

    courses = cursor.fetchall()

    # Support requests
    cursor.execute("""
        SELECT
            id,
            message,
            category,
            priority,
            department,
            status
        FROM support_requests
        WHERE student_id = ?
    """, (student_id,))

    support_requests = cursor.fetchall()

    # Schedule
    cursor.execute("""
        SELECT
            schedule.id,
            courses.name,
            schedule.day,
            schedule.start_time,
            schedule.end_time,
            schedule.room
        FROM schedule
        JOIN courses
        ON schedule.course_id = courses.id
        JOIN enrollments
        ON courses.id = enrollments.course_id
        WHERE enrollments.student_id = ?
    """, (student_id,))

    schedule = cursor.fetchall()

    connection.close()

    return {
        "student": {
            "id": student[0],
            "name": student[1],
            "email": student[2]
        },
        "courses": courses,
        "support_requests": support_requests,
        "schedule": schedule
    }


# ---------------- UPDATE COURSE PROGRESS ----------------

class ProgressUpdate(BaseModel):
    progress: int
    attendance: int


@app.put("/admin/enrollment/{enrollment_id}")
def update_enrollment(
    enrollment_id: int,
    data: ProgressUpdate
):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE enrollments
        SET
            progress = ?,
            attendance = ?
        WHERE id = ?
    """, (
        data.progress,
        data.attendance,
        enrollment_id
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Progress and attendance updated successfully"
    }


# ---------------- SCHEDULE ----------------

class Schedule(BaseModel):
    course_id: int
    day: str
    start_time: str
    end_time: str
    room: str


@app.post("/schedule")
def add_schedule(data: Schedule):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO schedule
        (
            course_id,
            day,
            start_time,
            end_time,
            room
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.course_id,
        data.day,
        data.start_time,
        data.end_time,
        data.room
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Schedule added successfully"
    }


# ---------------- ADMIN DASHBOARD ----------------



@app.get("/admin/dashboard")
def get_admin_dashboard():

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM enrollments")
    total_enrollments = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_requests
        WHERE status = 'Pending'
    """)
    pending_complaints = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_requests
        WHERE priority = 'High'
    """)
    high_priority_complaints = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_requests
        WHERE status = 'Resolved'
    """)
    resolved_complaints = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM support_requests
        WHERE status = 'In Progress'
    """)
    in_progress_complaints = cursor.fetchone()[0]

    connection.close()

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "pending_complaints": pending_complaints,
        "high_priority_complaints": high_priority_complaints,
        "resolved_complaints": resolved_complaints,
        "in_progress_complaints": in_progress_complaints
    }

# ---------------- UPDATE SUPPORT STATUS ----------------

class StatusUpdate(BaseModel):
    status: str


@app.put("/admin/support/{request_id}")
def update_support_status(
    request_id: int,
    data: StatusUpdate
):

    connection = sqlite3.connect("nexora.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE support_requests
        SET status = ?
        WHERE id = ?
    """, (
        data.status,
        request_id
    ))

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    if updated_rows == 0:
        return {
            "message": "Support request not found"
        }

    return {
        "message": "Support request status updated successfully",
        "request_id": request_id,
        "status": data.status
    }