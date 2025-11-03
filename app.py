# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os

# ---------------------------
# Flask App Initialization
# ---------------------------
app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

# ---------------------------
# Database setup
# ---------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'agri.db')

# Ensure database folder exists
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'database')):
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'))

# Initialize database if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Farmers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        )
    ''')
    
    # Plots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            crop_type TEXT,
            acreage REAL,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Flask-Login setup
# ---------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple in-memory user for demo
class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'admin': {'password': '1234'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ---------------------------
# Routes
# ---------------------------

# Home page - show farmers
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers")
    farmers = cursor.fetchall()
    conn.close()
    return render_template('index.html', farmers=farmers)

# Add farmer
@app.route('/add_farmer', methods=['GET', 'POST'])
@login_required
def add_farmer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO farmers (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_farmer.html')

# Add plot
@app.route('/add_plot', methods=['GET', 'POST'])
@login_required
def add_plot():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM farmers")
    farmers = cursor.fetchall()
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        crop_type = request.form['crop_type']
        acreage = request.form['acreage']
        cursor.execute("INSERT INTO plots (farmer_id, crop_type, acreage) VALUES (?, ?, ?)",
                       (farmer_id, crop_type, acreage))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('add_plot.html', farmers=farmers)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------------------
# Run the app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)