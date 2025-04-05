#!/bin/bash
# This script is used by Render.com to build the application

# Install Python dependencies
pip install -r requirements.txt

# Explicitly install gunicorn and matplotlib
pip install gunicorn==21.2.0
pip install matplotlib==3.7.2

# Print installed packages for debugging
pip list

# Create a symbolic link to ensure app.py points to app_noplots.py
echo "Creating symbolic link from app.py to app_noplots.py for compatibility"
ln -sf app_noplots.py app.py
