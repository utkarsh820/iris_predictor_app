# Deploying Iris Predictor App on PythonAnywhere

This guide will walk you through deploying the Iris Predictor app on PythonAnywhere.

## Step 1: Create a PythonAnywhere Account

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/) and sign up for a free account
2. Verify your email address

## Step 2: Upload Your Files

### Option 1: Using Git

1. Go to the "Consoles" tab and start a new Bash console
2. Clone your repository:
   ```
   git clone https://github.com/YOUR_USERNAME/iris-predictor-app.git
   ```

### Option 2: Manual Upload

1. Go to the "Files" tab
2. Create a new directory called `iris-predictor-app`
3. Navigate into the directory
4. Upload all your project files using the "Upload files" button

## Step 3: Set Up a Virtual Environment

1. Go to the "Consoles" tab and start a new Bash console
2. Navigate to your project directory:
   ```
   cd iris-predictor-app
   ```
3. Create a virtual environment:
   ```
   mkvirtualenv --python=python3.9 iris-env
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Step 4: Configure the Web App

1. Go to the "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.9
5. Enter the path to your project directory (e.g., `/home/YOUR_USERNAME/iris-predictor-app`)
6. Configure the WSGI file:
   - Click on the WSGI configuration file link
   - Replace the content with:
   ```python
   import sys
   import os
   
   # Add your project directory to the path
   path = '/home/YOUR_USERNAME/iris-predictor-app'
   if path not in sys.path:
       sys.path.append(path)
   
   # Import your app
   from app_noplots import app as application
   
   # Set environment variables
   os.environ['GOOGLE_API_KEY'] = 'your_google_api_key'
   os.environ['SECRET_KEY'] = 'your_secret_key'
   ```
   - Replace `YOUR_USERNAME` with your PythonAnywhere username
   - Replace `your_google_api_key` with your actual Google API key
   - Replace `your_secret_key` with a random string for Flask session encryption
   - Save the file

## Step 5: Configure Static Files

1. Go to the "Web" tab
2. Scroll down to "Static files"
3. Add a new static file mapping:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/iris-predictor-app/static`

## Step 6: Reload the Web App

1. Go to the "Web" tab
2. Click the "Reload" button for your web app

## Step 7: Visit Your Website

Your app should now be available at:
```
https://YOUR_USERNAME.pythonanywhere.com
```

## Troubleshooting

If you encounter issues:

1. Check the error logs in the "Web" tab
2. Make sure all files have the correct permissions
3. Verify that your virtual environment has all required packages
4. Check that your WSGI file is correctly configured

## Updating Your App

To update your app after making changes:

1. Upload the new files or pull the latest changes from Git
2. Go to the "Web" tab
3. Click the "Reload" button for your web app
