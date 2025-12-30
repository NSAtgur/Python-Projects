from flask import render_template,redirect,url_for,flash,session,request
from database import get_db
from decorators import login_required,role_required
from flask import Blueprint
import sqlite3

students_bp = Blueprint("students",__name__)


@students_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cur = db.cursor()

    total_students = cur.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
    present_students = cur.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Present' ").fetchone()[0]
    absent_students = cur.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Absent' ").fetchone()[0]


    return render_template('dashboard.html',total_students = total_students, present_students = present_students,absent_students = absent_students)


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
        
        db = get_db()
        cur = db.cursor()

        try:
            cur.execute("INSERT INTO students(name,roll) VALUES(?,?)",(name,roll))
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

        if not roll or not status:
            flash("Incomplete info!")
            return redirect(url_for('students.mark_attendance'))
        
        db = get_db()
        cur = db.cursor()

        cur.execute("INSERT INTO attendance (roll,status) VALUES(?,?) ",(roll,status))
        db.commit()
            
        
    return render_template('mark_attendance.html')
