from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os
from collections import defaultdict

# Initialize Flask app
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

@app.route("/", methods=["GET", "POST"])
def index():
    # Get client IP address
    ip_address = request.remote_addr
    
    # Get remaining requests
    remaining_requests = get_remaining_requests(ip_address)
    
    prediction = None
    description = None
    
    iris_descriptions = {
        "Iris Setosa": "Setosa has short petals and a compact structure, commonly found in grassy fields.",
        "Iris Versicolor": "Versicolor has medium-sized petals with a blend of blue and violet shades.",
        "Iris Virginica": "Virginica is a larger variant with deep purple petals found in wetlands."
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

            if prediction:
                description = iris_descriptions.get(prediction, "No description available.")
                
        except ValueError:
            prediction = "Error: Please enter valid numbers for all fields."
        except Exception as e:
            prediction = f"An unexpected error occurred: {str(e)}"
    
    # Return the template
    return render_template("index_simple.html",
                         prediction=prediction,
                         description=description,
                         remaining_requests=remaining_requests)

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
        
        # Simplified response without using the AI model
        return jsonify({
            'success': True,
            'answer': f"This is a simplified version of the app. The AI model is currently disabled to conserve resources. Your question was: '{question}'"
        })
                
    except Exception as e:
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
        'app_version': '1.0.2-simplified',
        'python_version': os.environ.get('PYTHON_VERSION', 'unknown')
    })

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
