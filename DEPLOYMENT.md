# Deploying Iris Predictor App

This guide explains how to deploy the Iris Predictor app on both PythonAnywhere and Render.com.

## Deployment on PythonAnywhere

### Step 1: Set Up Your PythonAnywhere Account
1. Create an account at [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. Go to the Web tab and create a new web app
3. Choose "Manual configuration" and Python 3.9

### Step 2: Upload Your Files
1. Use the Files tab to upload your project files
2. Or use Git to clone your repository

### Step 3: Configure the WSGI File
Edit your WSGI file (linked from the Web tab) to contain:

```python
import sys
import os

# Add your project directory to the path
path = '/home/yourusername/iris_predictor_app'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'your_google_api_key'
os.environ['SECRET_KEY'] = 'your_secret_key'

# Import your application
from app_noplots import application
```

### Step 4: Set Up Virtual Environment
1. Create a virtual environment: `mkvirtualenv --python=python3.9 iris-env`
2. Install dependencies: `pip install -r requirements.txt`
3. Note: The requirements.txt includes gunicorn which is needed for Render.com but not strictly required for PythonAnywhere

### Step 5: Configure Web App
1. Set the path to your virtual environment in the Web tab
2. Configure static files mapping for the static directory
3. Click "Reload" to start your app

## Deployment on Render.com

### Step 1: Create a Render Account
1. Sign up at [Render.com](https://render.com/)
2. Connect your GitHub repository

### Step 2: Create a New Web Service
1. Choose your repository
2. Set the name to "iris-predictor"
3. Choose "Python" as the environment

### Step 3: Configure Build Settings
1. Build Command: `chmod +x build.sh && ./build.sh`
2. Start Command: `gunicorn app_noplots:application`
3. Alternatively, you can use the provided `render.yaml` file for automatic configuration

### Step 4: Add Environment Variables
1. Add `GOOGLE_API_KEY` with your Google API key
2. Add `SECRET_KEY` with a random string

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for the deployment to complete

## Troubleshooting

### PythonAnywhere Issues
- If the AI feature doesn't work, whitelist `generativelanguage.googleapis.com` in the Web tab
- Check error logs in the Web tab

### Render.com Issues
- If you see 502 errors, check the logs for memory issues
- Try increasing the instance size if needed

## Switching Between Versions

The app has three versions:
- `app.py` - Full version with plotting (for local development)
- `app_noplots.py` - Version without plotting for PythonAnywhere
- `app_render.py` - Version specifically optimized for Render.com

All versions maintain the same core functionality but with different dependencies and optimizations for each platform.
