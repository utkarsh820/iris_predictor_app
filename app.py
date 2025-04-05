"""This file is a simple redirect to app_render.py.
It's used to ensure compatibility with platforms that might try to import from app.py
"""

# Import the application from app_render.py
from app_render import app, application

# This ensures that 'from app import app' and 'from app import application' both work
if __name__ == "__main__":
    app.run()
