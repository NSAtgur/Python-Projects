from flask import render_template,url_for,redirect,flash,session,request
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
import sqlite3
from datetime import datetime


auth_bp = Blueprint("auth",__name__)


@auth_bp.route('/')
def start():
    return render_template('start.html')


@auth_bp.route('/register',methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role =request.form.get('role')
        
        if not username or not password or not role:
            flash("Incomplete data")
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        db = get_db()
        cur = db.cursor()

        try:
            cur.execute("INSERT INTO users (username,password,role) VALUES(?,?,?)",(username,hashed_password,role))
            db.commit()

        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect(url_for('auth.register'))
        
        flash("User registered successfully. Please login!")
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method== 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Enter the credentials!")
            return redirect(url_for('auth.login'))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=?",(username,))
        row = cur.fetchone()

        if row and check_password_hash(row['password'],password):
            session['username'] = row['username']
            action = "Logged in"
            session['role'] = row['role']
            cur.execute("INSERT INTO audit_log(username, action, timestamp) VALUES(?,?,?)",(username, action,timestamp))
            db.commit()
            flash("Logged in !")
            return redirect(url_for('students.dashboard'))
        
        else:
            action = "failed to login"
            cur.execute("INSERT INTO audit_log(username,action,timestamp) VALUES(?,?,?)",(username, action,timestamp))
            db.commit()
            flash("Invalid Credentials")
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    username = session.get('username')
    if username:
        action = "logged out "
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO audit_log(username,action,timestamp) VALUES(?,?,?)",(username,action,timestamp))
        db.commit()
    session.clear()
    flash("Logged Out!")
    return redirect(url_for('auth.start'))

