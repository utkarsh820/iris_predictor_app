#!/bin/bash
# This script is used by Render.com to build the application

# Install Python dependencies
pip install -r requirements.txt

# Explicitly install gunicorn
pip install gunicorn==21.2.0

# Print installed packages for debugging
pip list

# Make sure the script has proper permissions
chmod +x app_render.py

# Print confirmation
echo "Build completed successfully. Using app.py (which imports from app_render.py) for deployment."
