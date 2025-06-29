# 🚀 Deploy SSM Health Facility Map to Render

This guide will walk you through deploying your secure facility map to Render, a modern cloud platform that's perfect for Flask apps.

## ✨ **Why Render?**

✅ **Free tier available**  
✅ **Automatic HTTPS**  
✅ **Easy deployment from GitHub**  
✅ **No server management**  
✅ **Built-in CI/CD**  
✅ **Custom domains**  

## 📋 **Prerequisites**

1. **GitHub account** (to host your code)
2. **Render account** (free at render.com)
3. **Your map files** (already created)

## 🚀 **Step-by-Step Deployment**

### **Step 1: Prepare Your Code for GitHub**

1. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SSM Health Facility Map"
   ```

2. **Create a GitHub repository:**
   - Go to github.com
   - Click "New repository"
   - Name it: `ssm-health-facility-map`
   - Make it private (recommended for sensitive data)
   - Don't initialize with README

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ssm-health-facility-map.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Deploy to Render**

1. **Go to Render Dashboard:**
   - Visit [render.com](https://render.com)
   - Sign up/Login
   - Click "New +"

2. **Create Web Service:**
   - Select "Web Service"
   - Connect your GitHub repository
   - Choose `ssm-health-facility-map`

3. **Configure the Service:**
   - **Name:** `ssm-health-facility-map`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn deploy_secure_map:app`
   - **Plan:** Free (or paid for more resources)

4. **Set Environment Variables:**
   Click "Environment" tab and add:
   ```
   MAP_USERNAME = ssm_team
   MAP_PASSWORD = your_secure_password_here
   FLASK_ENV = production
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait 2-3 minutes for deployment to complete

### **Step 3: Access Your Deployed App**

- **URL:** `https://your-app-name.onrender.com`
- **Username:** `ssm_team`
- **Password:** `your_secure_password_here`

## 🔧 **Customization Options**

### **Change App Name**
Edit `render.yaml`:
```yaml
name: your-custom-app-name
```

### **Add Custom Domain**
1. Go to your Render service
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records

### **Environment-Specific Settings**
Add to `render.yaml`:
```yaml
envVars:
  - key: MAP_USERNAME
    value: ssm_team
  - key: MAP_PASSWORD
    value: your_secure_password_here
  - key: FLASK_ENV
    value: production
```

## 🔒 **Security Best Practices**

### **For Production Use:**

1. **Use Strong Passwords:**
   ```bash
   # Generate a secure password
   openssl rand -base64 32
   ```

2. **Enable Auto-Deploy:**
   - Render automatically deploys when you push to GitHub
   - Keep your repository private

3. **Monitor Access:**
   - Check Render logs for suspicious activity
   - Consider adding IP whitelisting

4. **Regular Updates:**
   - Keep dependencies updated
   - Monitor security advisories

## 📊 **Monitoring & Maintenance**

### **View Logs:**
- Go to your Render service
- Click "Logs" tab
- Monitor for errors or issues

### **Update Your App:**
```bash
# Make changes locally
git add .
git commit -m "Update facility map"
git push origin main
# Render automatically redeploys
```

### **Scale Your App:**
- Free tier: 750 hours/month
- Paid plans: Unlimited hours, more resources

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **Build Fails:**
   - Check `requirements.txt` for missing dependencies
   - Verify Python version compatibility

2. **App Won't Start:**
   - Check logs for error messages
   - Verify `gunicorn` is in requirements.txt

3. **Login Issues:**
   - Verify environment variables are set correctly
   - Check username/password in Render dashboard

4. **Map Not Loading:**
   - Ensure `ssm_health_simple_color_coded_map.html` is in the repository
   - Check file permissions

### **Get Help:**
- Render Documentation: [docs.render.com](https://docs.render.com)
- Render Community: [community.render.com](https://community.render.com)

## 💰 **Costs**

- **Free Tier:** $0/month (750 hours)
- **Paid Plans:** Starting at $7/month
- **Custom Domains:** Free
- **SSL Certificates:** Free

## 🎉 **You're Done!**

Your SSM Health Facility Map is now:
- ✅ **Securely deployed** with HTTPS
- ✅ **Password protected**
- ✅ **Accessible worldwide**
- ✅ **Automatically updated** when you push changes
- ✅ **Monitored and maintained** by Render

**Share with your team:** `https://your-app-name.onrender.com`

---

**Need help?** Check the troubleshooting section or contact Render support! 