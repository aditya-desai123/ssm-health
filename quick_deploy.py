#!/usr/bin/env python3
"""
Quick Deployment Script for SSM Health Facility Map
Helps set up the secure server with custom credentials
"""

import hashlib
import os
import sys
import subprocess

def generate_password_hash(password):
    """Generate SHA256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_deploy_script(password_hash, username):
    """Update the deploy script with the new password hash and username"""
    with open('deploy_secure_map.py', 'r') as f:
        content = f.read()
    
    # Replace the password hash
    old_hash = "hashlib.sha256(\"your_secure_password_here\".encode()).hexdigest()"
    new_hash = f"hashlib.sha256(\"***HIDDEN***\".encode()).hexdigest()"
    
    content = content.replace(old_hash, new_hash)
    
    # Update both USERNAME and PASSWORD_HASH lines
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('USERNAME = '):
            lines[i] = f'USERNAME = "{username}"'
        elif line.strip().startswith('PASSWORD_HASH = '):
            lines[i] = f'PASSWORD_HASH = "{password_hash}"'
    
    with open('deploy_secure_map.py', 'w') as f:
        f.write('\n'.join(lines))

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import pandas
        import folium
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    print("🚀 SSM Health Facility Map - Quick Deployment")
    print("=" * 50)
    
    # Check if map file exists
    if not os.path.exists('ssm_health_simple_color_coded_map.html'):
        print("❌ Map file not found!")
        print("Please run 'python3 simple_color_coded_map.py' first to generate the map.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("Installing missing dependencies...")
        if not install_dependencies():
            return
    
    # Get credentials
    print("\n🔐 Set up secure access credentials:")
    username = input("Username (default: ssm_team): ").strip() or "ssm_team"
    password = input("Password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return
    
    # Confirm password
    confirm_password = input("Confirm password: ").strip()
    if password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    # Generate password hash
    password_hash = generate_password_hash(password)
    
    # Update deploy script
    update_deploy_script(password_hash, username)
    
    # Get port
    port = input("Port (default: 8080): ").strip() or "8080"
    
    # Update port in deploy script
    with open('deploy_secure_map.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('PORT = '):
            lines[i] = f'PORT = {port}'
            break
    
    with open('deploy_secure_map.py', 'w') as f:
        f.write('\n'.join(lines))
    
    print("\n✅ Configuration complete!")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    print(f"🌐 Port: {port}")
    
    # Start server
    print(f"\n🚀 Starting secure server on port {port}...")
    print("Press Ctrl+C to stop the server")
    print(f"\n🌐 Access your map at: http://localhost:{port}")
    
    try:
        subprocess.run([sys.executable, 'deploy_secure_map.py'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main() 