from flask import Flask, render_template, request, session, make_response, jsonify
import traceback  # For more detailed error logging
from io import BytesIO
import base64
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import google.generativeai as genai  # Add this import
from collections import defaultdict

# Load environment variables from .env file
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model with error handling
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Successfully initialized Gemini 2.0 Flash model")  # Add logging for confirmation

    # Test the model with a simple prompt to verify it's working
    try:
        test_response = model.generate_content("Hello")
        print("Model test successful")
    except Exception as e:
        print(f"Model test failed: {str(e)}")
        # Don't raise here, just log the error
        # This allows the app to start even if the model test fails
        # The /ask endpoint will handle errors separately
except Exception as e:
    print(f"Error initializing Gemini model: {str(e)}")  # Detailed error logging
    # Don't raise here, just log the error
    # Define a placeholder model that will return an error message
    class PlaceholderModel:
        def generate_content(self, *args, **kwargs):
            class PlaceholderResponse:
                text = "Sorry, the AI model is currently unavailable. Please try again later."
            return PlaceholderResponse()
    model = PlaceholderModel()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# Rate limiting configuration
API_RATE_LIMIT = 5  # 5 requests per day
api_usage = defaultdict(list)  # IP -> list of timestamps

def is_rate_limited(ip_address):
    """Check if the IP address has exceeded the rate limit"""
    global api_usage

    # Get current time
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Clean up old entries
    api_usage[ip_address] = [ts for ts in api_usage[ip_address] if ts >= today_start]

    # Check if rate limit is exceeded
    if len(api_usage[ip_address]) >= API_RATE_LIMIT:
        return True

    # Add current timestamp
    api_usage[ip_address].append(now)
    return False

def get_remaining_requests(ip_address):
    """Get the number of remaining requests for the IP address"""
    global api_usage

    # Get current time
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Clean up old entries
    api_usage[ip_address] = [ts for ts in api_usage[ip_address] if ts >= today_start]

    # Calculate remaining requests
    return max(0, API_RATE_LIMIT - len(api_usage[ip_address]))

def calculate_confidence(measurements):
    # Simple confidence calculation based on how far from decision boundaries
    pl = measurements['pl']
    if pl < 2.5:
        confidence = min(100, max(0, (2.5 - pl) / 2.5 * 100))
    elif pl < 4.8:
        confidence = min(100, max(0, (4.8 - pl) / 2.3 * 100))
    else:
        confidence = min(100, max(0, (pl - 4.8) / 2.0 * 100))
    return round(confidence, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    if 'history' not in session:
        session['history'] = []

    prediction = None
    description = None
    video_url = None

    # Get client IP address
    ip_address = request.remote_addr

    # Get remaining requests
    remaining_requests = get_remaining_requests(ip_address)

    iris_descriptions = {
        "Iris Setosa": "Setosa has short petals and a compact structure, commonly found in grassy fields.",
        "Iris Versicolor": "Versicolor has medium-sized petals with a blend of blue and violet shades.",
        "Iris Virginica": "Virginica is a larger variant with deep purple petals found in wetlands."
    }

    iris_videos = {
        "Iris Setosa": "https://www.youtube.com/embed/08u4Z8Po5mQ?autoplay=1",
        "Iris Versicolor": "https://www.youtube.com/embed/ScTaR_FPWWg?autoplay=1",
        "Iris Virginica": "https://www.youtube.com/embed/nCYUzkil2xQ?autoplay=1"
    }

    if request.method == "POST":
        try:
            sl = float(request.form["sl"])
            sw = float(request.form["sw"])
            pl = float(request.form["pl"])
            pw = float(request.form["pw"])

            if pl < 2.5:
                prediction = "Iris Setosa"
            elif pl < 4.8:
                prediction = "Iris Versicolor"
            else:
                prediction = "Iris Virginica"

            if prediction and 'Error' not in prediction:
                description = iris_descriptions.get(prediction, "No description available.")
                video_url = iris_videos.get(prediction)

                # Add to history
                history_entry = {
                    'measurements': {'sl': sl, 'sw': sw, 'pl': pl, 'pw': pw},
                    'prediction': prediction,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                session['history'].append(history_entry)
                session.modified = True

        except ValueError:
            prediction = "Error: Please enter valid numbers for all fields."
        except Exception as e:
            prediction = f"An unexpected error occurred: {e}"
            traceback.print_exc()

    # Always return the template, regardless of method or prediction status
    return render_template("index_noplots.html",
                         prediction=prediction,
                         description=description,
                         video_url=video_url,
                         remaining_requests=remaining_requests)

@app.route("/export")
def export():
    import csv
    from io import StringIO

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Timestamp', 'Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width', 'Prediction'])

    for entry in session.get('history', []):
        cw.writerow([
            entry['timestamp'],
            entry['measurements']['sl'],
            entry['measurements']['sw'],
            entry['measurements']['pl'],
            entry['measurements']['pw'],
            entry['prediction']
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=iris_predictions.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/ask", methods=["POST"])
def ask_question():
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Request must be JSON'
        }), 400

    # Get client IP address
    ip_address = request.remote_addr

    # Check rate limit
    if is_rate_limited(ip_address):
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded. You can only make 5 requests per day.'
        }), 429

    try:
        question = request.json.get('question')
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400

        # Enhanced context focusing on botanical and biological aspects
        context = """
        You are a botanical expert specializing in iris flowers and plant biology. Focus on:

        1. Iris Species Information:
        - Iris Setosa: Small petals, compact structure, adapted to grassy fields, distinctive blue-violet flowers
        - Iris Versicolor: Medium-sized petals, blue-violet coloration, found in mixed habitats
        - Iris Virginica: Large petals, deep purple coloration, typically found in wetland environments

        2. Botanical Features:
        - Sepal: Modified leaves that protect the flower bud
        - Petal: Colored parts of the flower that attract pollinators
        - Key measurements: Sepal length/width, Petal length/width

        3. Biological Context:
        - Plant taxonomy
        - Growth patterns
        - Environmental adaptations
        - Reproductive strategies
        - Ecological relationships

        Provide clear, accurate, and scientific information while keeping explanations accessible.

        Question: """

        full_prompt = context + question

        try:
            print(f"Attempting to call Gemini API with question: {question[:50]}...")

            # Try to use the API with fallback mechanism
            try:
                # Simplified model generation call with more conservative settings
                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=500  # Limit response length to save memory
                )

                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )

                if response and hasattr(response, 'text'):
                    answer = response.text.strip()
                    # Clean up the response
                    answer = answer.replace('<', '&lt;').replace('>', '&gt;')

                    print("Successfully received response from Gemini API")
                    return jsonify({
                        'success': True,
                        'answer': answer
                    })
                else:
                    print("API returned invalid response format")
                    raise Exception("Invalid response format from API")

            except Exception as api_error:
                print(f"API call failed: {str(api_error)}")

                # Fallback to pre-defined responses
                print("Using fallback response system")
                fallback_responses = {
                    "setosa": "Iris setosa is a species of iris with distinctive small, compact flowers and short petals (less than 2.5cm). It's commonly found in grassy fields and is one of the three species in the famous Iris dataset.",
                    "versicolor": "Iris versicolor has medium-sized petals (between 2.5-4.8cm) with blue-violet coloration. It's found in mixed habitats and is one of the three species in the famous Iris dataset.",
                    "virginica": "Iris virginica has large petals (greater than 4.8cm) with deep purple coloration. It's typically found in wetland environments and is one of the three species in the famous Iris dataset.",
                    "identify": "Iris species can be identified by measuring their sepal and petal dimensions. Setosa has short petals (< 2.5cm), Versicolor has medium petals (2.5-4.8cm), and Virginica has longer petals (> 4.8cm).",
                    "difference": "The main differences between iris species are in their petal and sepal measurements. Setosa has short petals, Versicolor has medium-sized petals, and Virginica has longer petals. They also differ in habitat preference and flower coloration.",
                    "grow": "Iris flowers generally prefer moist, well-drained soil and full to partial sun. They're perennials that bloom in spring to early summer. Different species have different specific requirements - Setosa prefers drier conditions, while Virginica thrives in wetter environments.",
                    "care": "To care for iris plants: plant in well-drained soil, provide adequate water (especially during blooming), divide overcrowded rhizomes every 3-5 years, remove dead foliage in fall, and protect from iris borers and rot by ensuring good air circulation."
                }

                # Look for keywords in the question
                question_lower = question.lower()
                for keyword, response in fallback_responses.items():
                    if keyword in question_lower:
                        return jsonify({
                            'success': True,
                            'answer': response + "\n\n(Note: This is a pre-defined response as the AI service couldn't be reached. PythonAnywhere's free tier has limited external API access.)"
                        })

                # Default fallback response
                return jsonify({
                    'success': True,
                    'answer': "I'm sorry, but I couldn't connect to the AI service. PythonAnywhere's free tier has limited external API access.\n\nThe Iris Predictor can still classify iris flowers based on measurements. For basic information: Setosa has short petals (<2.5cm), Versicolor has medium petals (2.5-4.8cm), and Virginica has longer petals (>4.8cm)."
                })

        except Exception as model_error:
            print(f"Model generation error: {str(model_error)}")
            return jsonify({
                'success': False,
                'error': f'Error generating response: {str(model_error)}'
            }), 500

    except Exception as e:
        print(f"Error in /ask endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

# Add a route to check API usage
@app.route("/api-status")
def api_status():
    ip_address = request.remote_addr
    remaining = get_remaining_requests(ip_address)
    return jsonify({
        'ip_address': ip_address,
        'remaining_requests': remaining,
        'limit': API_RATE_LIMIT,
        'reset_time': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    })

# Add a simple health check endpoint
@app.route("/health")
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'app_version': '1.0.1-noplots',
        'python_version': os.environ.get('PYTHON_VERSION', 'unknown')
    })

# Add a test endpoint for the AI API
@app.route("/test-ai")
def test_ai():
    try:
        # Get API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_API_KEY environment variable not set',
                'env_vars': list(os.environ.keys())  # List available env vars (safe ones only)
            })

        # Try to configure the API
        try:
            genai.configure(api_key=api_key)
            print("API configured successfully")
        except Exception as config_error:
            return jsonify({
                'success': False,
                'error': f'API configuration error: {str(config_error)}'
            })

        # Try to initialize the model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("Model initialized successfully")
        except Exception as model_error:
            return jsonify({
                'success': False,
                'error': f'Model initialization error: {str(model_error)}'
            })

        # Try a simple generation
        try:
            response = model.generate_content("What is an Iris flower? Answer in one sentence.")
            print("Content generated successfully")
            answer = response.text if hasattr(response, 'text') else 'No text attribute'
            return jsonify({
                'success': True,
                'message': 'API test successful',
                'response': answer
            })
        except Exception as generate_error:
            return jsonify({
                'success': False,
                'error': f'Content generation error: {str(generate_error)}'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'General error: {str(e)}'
        })

# Detect the platform we're running on
def is_pythonanywhere():
    """Check if we're running on PythonAnywhere"""
    return 'PYTHONANYWHERE_SITE' in os.environ

def is_render():
    """Check if we're running on Render.com"""
    return 'RENDER' in os.environ

# Platform-specific configurations
def configure_for_platform():
    """Apply platform-specific configurations"""
    if is_pythonanywhere():
        print("Running on PythonAnywhere - applying specific configurations")
        # PythonAnywhere specific configurations can go here
        pass

    elif is_render():
        print("Running on Render.com - applying specific configurations")
        # Render.com specific configurations can go here
        pass

    else:
        print("Running on local/other environment")

# Apply platform-specific configurations
configure_for_platform()

# This allows the app to be imported by WSGI servers
application = app

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Run the app - ensure proper binding for production environments
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Error starting the application: {str(e)}")
        # Try alternative port if specified port is unavailable
        alt_port = int(os.environ.get("ALTERNATIVE_PORT", 8080))
        print(f"Attempting to start on alternative port {alt_port}")
        app.run(host='0.0.0.0', port=alt_port, debug=False)
