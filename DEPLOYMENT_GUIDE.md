# 🚀 SSM Health Facility Map - Deployment Guide

This guide provides multiple options for securely deploying your SSM Health facility map for team access.

## 🔐 **Option 1: Simple Password-Protected Server (Recommended)**

### Quick Setup (Local/Internal Network)

1. **Install Dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Change the Password:**
   Edit `deploy_secure_map.py` and change the password:
   ```python
   # Replace "your_secure_password_here" with your actual password
   PASSWORD_HASH = hashlib.sha256("your_actual_password".encode()).hexdigest()
   ```

3. **Start the Server:**
   ```bash
   python3 deploy_secure_map.py
   ```

4. **Access the Map:**
   - Open browser to: `http://localhost:8080`
   - Username: `ssm_team`
   - Password: `your_actual_password`

### For Team Access (Internal Network)

1. **Find your computer's IP address:**
   ```bash
   # On Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig
   ```

2. **Team members access via:**
   `http://YOUR_IP_ADDRESS:8080`

## ☁️ **Option 2: Cloud Deployment (More Secure)**

### AWS EC2 Deployment

1. **Launch EC2 Instance:**
   - Choose Ubuntu Server 20.04 LTS
   - t3.micro (free tier) or larger
   - Configure Security Group to allow port 8080

2. **Connect and Setup:**
   ```bash
   # Connect to your instance
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and pip
   sudo apt install python3 python3-pip -y
   
   # Upload your files (use scp or git)
   scp -r /path/to/your/project ubuntu@your-instance-ip:~/
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Start server
   python3 deploy_secure_map.py
   ```

3. **Access via:** `http://YOUR_EC2_IP:8080`

### Heroku Deployment

1. **Create Heroku App:**
   ```bash
   # Install Heroku CLI
   # Create app
   heroku create your-ssm-map-app
   
   # Deploy
   git add .
   git commit -m "Deploy SSM Health Map"
   git push heroku main
   ```

2. **Set Environment Variables:**
   ```bash
   heroku config:set FLASK_SECRET_KEY=your_secret_key
   heroku config:set MAP_USERNAME=ssm_team
   heroku config:set MAP_PASSWORD=your_password
   ```

## 🔒 **Option 3: Enterprise-Grade Security**

### With HTTPS and Advanced Authentication

1. **Use Nginx as Reverse Proxy:**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Add Multi-Factor Authentication:**
   - Integrate with Google Authenticator
   - Use SMS-based 2FA
   - Implement IP whitelisting

### Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8080
   CMD ["python3", "deploy_secure_map.py"]
   ```

2. **Build and Run:**
   ```bash
   docker build -t ssm-map .
   docker run -p 8080:8080 ssm-map
   ```

## 📋 **Security Checklist**

- [ ] Change default password
- [ ] Use HTTPS in production
- [ ] Implement session timeout
- [ ] Add IP whitelisting if needed
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup data regularly

## 🛠️ **Customization Options**

### Change Port
Edit `deploy_secure_map.py`:
```python
PORT = 9000  # Change to your preferred port
```

### Add Multiple Users
```python
USERS = {
    "admin": hashlib.sha256("admin_pass".encode()).hexdigest(),
    "analyst": hashlib.sha256("analyst_pass".encode()).hexdigest(),
    "viewer": hashlib.sha256("viewer_pass".encode()).hexdigest()
}
```

### Session Timeout
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
```

## 🚨 **Important Security Notes**

1. **Never commit passwords to version control**
2. **Use environment variables for production**
3. **Regularly rotate passwords**
4. **Monitor access logs**
5. **Keep dependencies updated**
6. **Use HTTPS in production environments**

## 📞 **Support**

For deployment issues or security questions, refer to your IT team or security policies.

---

**⚠️ Disclaimer:** This deployment guide provides basic security measures. For production use with sensitive healthcare data, consult with your organization's security team and ensure compliance with relevant regulations (HIPAA, etc.). 