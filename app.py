from flask import Flask, render_template, request, redirect, url_for, Response
import mysql.connector
import csv

app = Flask(__name__)

# Database configuration (centralized)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Nayan@2775',  # Correct password from your test.py
    'database': 'attendance_db'
}

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Initialize the database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        student_id INT, 
        subject_id INT, 
        status VARCHAR(20), 
        date DATE, 
        FOREIGN KEY(student_id) REFERENCES students(id), 
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return render_template('index.html', students=students, subjects=subjects)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_subject', methods=['POST'])
def add_subject():
    name = request.form['name']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    status = request.form['status']
    date = request.form['date']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, subject_id, status, date) VALUES (%s, %s, %s, %s)", 
                   (student_id, subject_id, status, date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/attendance_report', methods=['GET', 'POST'])
def attendance_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    student_id = request.form.get('student_id')
    subject_id = request.form.get('subject_id')
    date = request.form.get('date')

    query = """
        SELECT students.name, subjects.name, attendance.status, attendance.date
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        JOIN subjects ON attendance.subject_id = subjects.id
        WHERE 1 = 1
    """
    params = []
    if student_id:
        query += " AND attendance.student_id = %s"
        params.append(student_id)
    if subject_id:
        query += " AND attendance.subject_id = %s"
        params.append(subject_id)
    if date:
        query += " AND attendance.date = %s"
        params.append(date)

    query += " ORDER BY attendance.date DESC"
    cursor.execute(query, params)
    report = cursor.fetchall()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    conn.close()
    return render_template('report.html', report=report, students=students, subjects=subjects)

@app.route('/export_report')
def export_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT students.name, subjects.name, attendance.status, attendance.date
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        JOIN subjects ON attendance.subject_id = subjects.id
        ORDER BY attendance.date DESC
    """)
    report = cursor.fetchall()
    conn.close()

    output = [['Student Name', 'Subject', 'Status', 'Date']]
    output.extend(report)

    response = Response('\n'.join([','.join(map(str, row)) for row in output]), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=attendance_report.csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)