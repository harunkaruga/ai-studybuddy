# 🚀 AI Study Buddy - Deployment Guide

## 📋 **Quick Fixes for Common Deployment Issues**

### 🔧 **Issue 1: Signup/Login Not Working**

**Problem**: Forms submit but nothing happens, no response from server

**Solutions**:
1. **Check CORS**: Make sure your deployment platform allows CORS
2. **Check Console**: Open browser dev tools (F12) and look for errors
3. **Test Endpoints**: Visit `/debug` endpoint to see if server is running
4. **Check Logs**: Look at your deployment platform's logs

### 🌐 **Issue 2: CORS Errors**

**Problem**: Browser blocks requests due to CORS policy

**Solution**: The app now includes `flask-cors` to handle this automatically

### 📱 **Issue 3: Mobile/Tablet Issues**

**Problem**: App doesn't work on mobile devices

**Solution**: The app is responsive and should work on all devices

## 🛠️ **Deployment Steps**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Run the App**
```bash
python demo.py
```

### **Step 3: Test Endpoints**
- Visit `/` - Main page
- Visit `/debug` - Debug information
- Visit `/status` - App status

## 🔍 **Troubleshooting**

### **Check if Server is Running**
Visit: `https://your-domain.com/debug`

Expected response:
```json
{
  "app_name": "AI Study Buddy Demo",
  "status": "running",
  "endpoints": ["/", "/auth/register", "/auth/login", ...]
}
```

### **Test Authentication**
1. Try to register a new user
2. Check browser console for errors
3. Check server logs for any errors

### **Common Error Messages**

- **"No data received"**: Frontend not sending data properly
- **"Authentication required"**: User not logged in
- **"Network error"**: Server not responding or CORS issue

## 📱 **Platform-Specific Notes**

### **Heroku**
- Add `flask-cors` to requirements.txt ✅
- Set environment variables if needed
- Check build logs for errors

### **Vercel**
- May need to configure CORS in vercel.json
- Check function logs for errors

### **Railway/Render**
- Should work out of the box with flask-cors ✅
- Check deployment logs

### **Local Development**
- Run `python demo.py`
- Visit `http://localhost:5000`

## 🆘 **Still Having Issues?**

1. **Check the `/debug` endpoint** - shows all available routes
2. **Check browser console** - shows JavaScript errors
3. **Check server logs** - shows backend errors
4. **Test with simple tools** like Postman or curl

## 📞 **Support**

If you're still having issues:
1. Check the `/debug` endpoint output
2. Share any error messages from browser console
3. Share any error messages from server logs
4. Try the app locally first with `python demo.py`
