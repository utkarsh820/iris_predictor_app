# Iris Predictor App

A web application that predicts Iris flower species based on sepal and petal measurements. The app includes an AI-powered Q&A feature about Iris flowers using Google's Gemini API.

## App Versions

This repository contains multiple versions of the application to ensure compatibility with different hosting platforms:

- **app.py** - A simple redirect file that imports from app_render.py (for Render.com)
- **app_noplots.py** - A version without matplotlib plotting for PythonAnywhere
- **app_render.py** - A version specifically optimized for Render.com

All versions maintain the same core functionality but with different dependencies and optimizations for each platform.

## Features

- Predict Iris species (Setosa, Versicolor, or Virginica) based on measurements
- Visual representation of measurements with interactive charts
- AI-powered Q&A about Iris flowers and plant biology
- Rate limiting (5 API requests per day per IP address)
- Export prediction history to CSV

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI**: Google Gemini API
- **Deployment**: Compatible with both Render.com and PythonAnywhere

## Deployment Options

### Deployment on Render.com

#### Prerequisites

1. A [Render.com](https://render.com/) account
2. A Google API key for Gemini AI

#### Steps to Deploy

1. **Fork or clone this repository**

2. **Create a new Web Service on Render**
   - Go to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Name your service (e.g., "iris-predictor")
   - Set the Environment to "Python"
   - Set the Build Command to `chmod +x build.sh && ./build.sh`
   - Set the Start Command to `gunicorn app:application`

3. **Configure Environment Variables**
   - In the Render dashboard, go to your web service
   - Click on "Environment" tab
   - Add the following environment variables:
     - `GOOGLE_API_KEY`: Your Google API key for Gemini
     - `SECRET_KEY`: A random string for Flask session encryption

4. **Deploy the Service**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

5. **Access Your Application**
   - Once deployment is complete, you can access your application at the URL provided by Render

### Deployment on PythonAnywhere

#### Prerequisites

1. A [PythonAnywhere.com](https://www.pythonanywhere.com/) account
2. A Google API key for Gemini AI

#### Steps to Deploy

1. **Upload Your Files**
   - Use the Files tab to upload your project files
   - Or use Git to clone your repository

2. **Set Up a Virtual Environment**
   - Go to the "Consoles" tab and start a new Bash console
   - Navigate to your project directory
   - Create a virtual environment: `mkvirtualenv --python=python3.9 iris-env`
   - Install dependencies: `pip install -r requirements.txt`

3. **Configure the WSGI File**
   - Go to the Web tab and create a new web app
   - Choose "Manual configuration" and Python 3.9
   - Edit your WSGI file (linked from the Web tab) to contain:

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

4. **Configure Static Files**
   - In the Web tab, scroll down to "Static files"
   - Add a mapping for `/static/` to your static directory

5. **Reload Your Web App**
   - Click the "Reload" button in the Web tab

## API Rate Limiting

The application includes a rate limiting feature that restricts users to 5 AI requests per day per IP address. This is implemented using an in-memory storage that tracks API usage by IP address.

- The rate limit resets at midnight (server time)
- Users can see their remaining requests on the UI
- When the limit is reached, the AI button is disabled

## Troubleshooting

### PythonAnywhere Issues
- If the AI feature doesn't work, whitelist `generativelanguage.googleapis.com` in the Web tab
- Check error logs in the Web tab

### Render.com Issues
- If you see 502 errors, check the logs for memory issues
- Try increasing the instance size if needed

## Local Development

1. Clone the repository
2. Create a `.env` file with your `GOOGLE_API_KEY`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app_noplots.py` or `python app_render.py`
5. Access the application at `http://localhost:5000`

## License

MIT
