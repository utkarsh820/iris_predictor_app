"""
This file is a simple redirect to app_noplots.py.
It's used to ensure compatibility with platforms that might try to import from app.py
"""

# Import the application from app_noplots.py
from app_noplots import app, application

# This ensures that 'from app import app' and 'from app import application' both work
if __name__ == "__main__":
    app.run()
