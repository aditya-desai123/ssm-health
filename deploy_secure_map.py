#!/usr/bin/env python3
"""
Secure SSM Health Facility Map Server with Authentication
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
import os
from simple_color_coded_map import create_simple_color_coded_map

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configuration
USERNAME = os.environ.get('MAP_USERNAME', 'ssm_team')
PASSWORD = os.environ.get('MAP_PASSWORD', 'your_secure_password_here')
PORT = int(os.environ.get('PORT', 8080))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/map')
@login_required
def map_view():
    return send_from_directory('.', 'ssm_health_comprehensive_final_map.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    print("🔐 Starting secure SSM Health Facility Map server...")
    
    # Generate the comprehensive final map
    try:
        print("🗺️ Generating comprehensive final map...")
        from create_comprehensive_final_map import main as generate_map
        generate_map()
        print("✅ Comprehensive map generated successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not generate comprehensive map: {e}")
    
    print(f"🌐 Server will be available at: http://localhost:{PORT}")
    print(f"👤 Username: {USERNAME}")
    print(f"🔑 Password: {PASSWORD}")
    print("✅ Server is ready! Use the credentials above to log in.")
    
    app.run(host='0.0.0.0', port=PORT, debug=False) 