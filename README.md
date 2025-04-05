# Iris Predictor App

A web application that predicts Iris flower species based on sepal and petal measurements. The app includes an AI-powered Q&A feature about Iris flowers using Google's Gemini API.

## Important Note

This repository contains two versions of the application:
- `app.py` - The original version with all features including plotting
- `app_noplots.py` - A version without matplotlib plotting for easier deployment on PythonAnywhere

The application is configured to use `app_noplots.py` for deployment.

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
- **Visualization**: Matplotlib, Seaborn
- **Deployment**: Render.com

## Deployment to Render.com

### Prerequisites

1. A [Render.com](https://render.com/) account
2. A Google API key for Gemini AI

### Steps to Deploy

1. **Fork or clone this repository**

2. **Create a new Web Service on Render**
   - Go to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Name your service (e.g., "iris-predictor")
   - Set the Environment to "Python"
   - Set the Build Command to `pip install -r requirements.txt`
   - Set the Start Command to `gunicorn app:app`

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

## API Rate Limiting

The application includes a rate limiting feature that restricts users to 5 AI requests per day per IP address. This is implemented using an in-memory storage that tracks API usage by IP address.

- The rate limit resets at midnight (server time)
- Users can see their remaining requests on the UI
- When the limit is reached, the AI button is disabled

## Local Development

1. Clone the repository
2. Create a `.env` file with your `GOOGLE_API_KEY`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Access the application at `http://localhost:5000`

## License

MIT
