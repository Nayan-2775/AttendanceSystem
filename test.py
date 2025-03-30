import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Nayan@2775',  # Replace with what’s in your app.py
        database='attendance_db'
    )
    print("Connected successfully!")
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")