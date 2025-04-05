"""
This is a sample WSGI configuration file for PythonAnywhere.
Copy and paste the contents of this file into your PythonAnywhere WSGI configuration.
Make sure to replace 'yourusername' with your actual PythonAnywhere username
and add your actual Google API key.
"""

import sys
import os

# Add your project directory to the path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/iris_predictor_app'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'your_google_api_key'  # Replace with your actual API key
os.environ['SECRET_KEY'] = 'your_secret_key'  # Replace with a random string

# Import your application
from app_noplots import application
