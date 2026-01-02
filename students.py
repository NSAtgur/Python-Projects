from flask import render_template,redirect,url_for,flash,session,request
from database import get_db
from decorators import login_required,role_required
from flask import Blueprint
import sqlite3
import csv
from flask import Response
from io import StringIO
from datetime import datetime
import pytz


students_bp = Blueprint("students",__name__)

@students_bp.route('/dashboard')
@login_required
def dashboard():
    

    return render_template('dashboard.html')


@students_bp.route('/add_students',methods = ['GET','POST'])
@login_required 
@role_required('admin')
def add_students():
    if request.method == 'POST':
        name = request.form.get('name')
        roll = request.form.get('roll',type = int)

        if not name or not roll:
            flash("Data incomplete !")
            return redirect(url_for('students.add_students'))
        username = session['username']
        action = f"Added student (roll number:{roll})"
        timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))


        db = get_db()
        cur = db.cursor()

        try:
            cur.execute("INSERT INTO students(name,roll) VALUES(?,?)",(name,roll))
            cur.execute("INSERT INTO audit_log (username,action, timestamp) VALUES(?,?,?)",(username, action,timestamp))
            db.commit()

        except sqlite3.IntegrityError:
            flash("Student data already exists")
            return redirect(url_for('students.add_students'))
        
        
        flash("Student added successfully")
        return redirect(url_for('students.add_students'))
    
    return render_template('add_students.html')


@students_bp.route('/view_students')
@login_required
@role_required('admin')
def view_students():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    
    return render_template('view_students.html',students=students)


@students_bp.route('/mark_attendance',methods = ['GET','POST'])
@login_required
@role_required('admin')
def mark_attendance():
    if request.method == 'POST':
        roll = request.form.get('roll',type = int)
        status = request.form.get('status')
        date = request.form.get('date')

        username = session['username']
        action = f"Marked attendance (roll number:{roll})"
        timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))

        if not roll or not status or not date:
            flash("Incomplete info!")
            return redirect(url_for('students.mark_attendance'))
        
        db = get_db()
        cur = db.cursor()

        cur.execute("INSERT INTO attendance (roll,status,date) VALUES(?,?,?) ",(roll,status,date))
        cur.execute("INSERT INTO audit_log(username, action, timestamp) VALUES(?,?,?)",(username,action,timestamp))

        db.commit()
        flash("Attendance recorded successfully!")
        return redirect(url_for('students.mark_attendance'))
        
    return render_template('mark_attendance.html')


@students_bp.route('/view_attendance',methods = ['GET','POST'])
@login_required
@role_required('admin')
def view_attendance():
    total_count=0
    present_count=0
    percentage_attendance=0
    if request.method == 'POST':
        roll = request.form.get('roll',type = int)
        
        if not roll:
            flash("Enter the roll number")
            return redirect(url_for('students.view_attendance'))
        
        db = get_db()
        cur = db.cursor()
        present_count = cur.execute("SELECT COUNT(*) FROM attendance WHERE roll = ? AND status ='present' ",(roll,)).fetchone()[0]
        total_count = cur.execute("SELECT COUNT(*) FROM attendance WHERE roll = ? ORDER BY date",(roll,)).fetchone()[0]
        if total_count>0:
            percentage_attendance = (present_count/total_count)*100
        else:
            flash("attendance record not found!")
            return redirect(url_for('students.view_attendance'))
       
    return render_template('view_attendance.html', total_count=total_count, present_count=present_count,percentage_attendance=percentage_attendance)


@students_bp.route('/delete_student',methods = ['GET','POST'])
@login_required
@role_required('admin')
def delete_student():
    if request.method == 'POST':
        roll = request.form.get('roll',type=int)
        
        if not roll:
            flash("Incomplete data")
            return redirect(url_for('students.delete_student'))
        timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))

        username = session['username']
        action= f"Deleted student (roll number:{roll})"       

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE roll=?",(roll,))
        rows = cur.fetchone()
        
        if not rows:
            flash("Roll Number not in Database!")
            return redirect(url_for('students.delete_student'))
        
        cur.execute("DELETE FROM students WHERE roll=?",(roll,))
        cur.execute("DELETE FROM attendance WHERE roll=?",(roll,))
        cur.execute("INSERT INTO audit_log(username, action, timestamp) VALUES(?,?,?)",(username,action,timestamp))

        db.commit()

        flash("Student Deleted successfully")
        return redirect(url_for('students.delete_student'))
    return render_template('delete_student.html')


@students_bp.route('/edit_student',methods = ['GET','POST'])
@login_required
@role_required('admin')
def edit_student():
    if request.method == 'POST':
        name  = request.form.get('name')
        roll = request.form.get('roll',type=int)

        if not name or not roll:
            flash("Enter complete details!")
            return redirect(url_for('students.edit_student'))
        
        username = session['username']
        action = f"Edited student details (roll number:{roll})."
        timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE roll=?",(roll,))
        rows = cur.fetchone()

        if not rows:
            flash("Roll Number not in Database!")
            return redirect(url_for('students.edit_student'))
        
        cur.execute("UPDATE students SET name=? WHERE roll = ?",(name,roll))
        cur.execute("INSERT INTO audit_log(username, action,timestamp) VALUES(?,?,?)",(username,action,timestamp))
        db.commit()
        db.commit()
        
        flash("Student details edited successfully!")
        return redirect(url_for("students.edit_student"))
    
    return render_template('edit_student.html')

@students_bp.route('/export_students')
def export_students():
    username = session['username']
    action = "exported student details."
    db = get_db()
    cur = db.cursor()
    timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))

    cur.execute("SELECT * FROM students")
    cur.execute("INSERT INTO audit_log(username, action,timestamp) VALUES(?,?,?)",(username,action,timestamp))

    rows = cur.fetchall()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name','Roll Number'])
    for row in rows:
        writer.writerow([row['name'], row['roll']])
    
    return Response(output.getvalue(),mimetype = "text/csv", headers = {"Content-Disposition":"attachment; filename = students.csv"})


@students_bp.route('/audit_log')
@login_required
@role_required('admin')
def audit_log():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM audit_log")
    rows = cur.fetchall()
    return render_template('audit_log.html',rows=rows)


@students_bp.route('/clear_auditlog', methods = ['POST'])
@login_required
@role_required('admin')
def clear_auditlog():

    username = session.get('username')
    action = "Deleted the audit log."
    timestamp = datetime.now(pytz.timezone("Asia/Kolkata"))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM audit_log")
    cur.execute("INSERT INTO audit_log(username,action,timestamp) VALUES(?,?,?)",(username, action, timestamp))
    db.commit()

    flash("Audit logs deleted")
    return redirect(url_for('students.audit_log'))