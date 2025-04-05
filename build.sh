#!/bin/bash
# This script is used by Render.com to build the application

# Install Python dependencies
pip install -r requirements.txt

# Explicitly install gunicorn
pip install gunicorn==21.2.0

# Print installed packages for debugging
pip list
