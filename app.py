from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import re
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')

# Enable CORS for all routes (allows frontend to call API from different origins)
CORS(app)

# Global variables for models
vectorizer = None
category_model = None
type_model = None

def load_models():
    """Load ML models and vectorizer"""
    global vectorizer, category_model, type_model
    
    try:
        # Check if model files exist
        model_files = {
            'vectorizer': 'tfidf_vectorizer.pkl',
            'category_model': 'trained_model.pkl',
            'type_model': 'transaction_type_model.pkl'
        }
        
        missing_files = []
        for name, filepath in model_files.items():
            if not os.path.exists(filepath):
                missing_files.append(filepath)
        
        if missing_files:
            logger.error(f"Missing model files: {', '.join(missing_files)}")
            return False
        
        # Load models
        logger.info("Loading models...")
        vectorizer = joblib.load(model_files['vectorizer'])
        category_model = joblib.load(model_files['category_model'])
        type_model = joblib.load(model_files['type_model'])
        
        logger.info("✅ Models loaded successfully!")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        return False

def extract_amount(description):
    """Extract amount from transaction description using improved pattern matching"""
    if not description:
        return None
    
    try:
        text = str(description).lower()
        
        # Multiple patterns to catch different amount formats (ordered by specificity)
        patterns = [
            # Pattern 1: Currency directly attached to number (e.g., "rs31720", "inr5000")
            r'(?:rs|inr|₹)(\d+(?:,\d{3})*(?:\.\d+)?)',
            
            # Pattern 2: Currency with space/dot followed by amount (e.g., "rs 5000", "INR 10,000")
            r'(?:rs|inr|₹)\.?\s+(\d+(?:,\d{3})*(?:\.\d+)?)',
            
            # Pattern 3: Numbers after amount-related keywords (e.g., "by 900", "debited by 900.0")
            r'(?:by|of|amount|value|total|sum|paid|transferred|credited|debited)\s+(\d+(?:,\d{3})*(?:\.\d{1,2})?)',
            
            # Pattern 4: Amount with commas (e.g., "10,000", "1,23,456.78")
            r'\b(\d{1,2}(?:,\d{2})*(?:,\d{3})?(?:\.\d+)?|\d{1,3}(?:,\d{3})+(?:\.\d+)?)\b',
            
            # Pattern 5: Number with decimals (e.g., "500.50", "1000.00", "900.0")
            r'\b(\d+\.\d{1,2})\b',
            
            # Pattern 6: Large standalone numbers (4+ digits to avoid dates like "24", "2025")
            r'\b(\d{4,})\b'
        ]
        
        # Try each pattern in order
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    return abs(amount)
                except (ValueError, AttributeError):
                    continue
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting amount: {e}")
        return None

def preprocess_description(description):
    """Preprocess description same as training"""
    try:
        desc_lower = str(description).lower().strip()
        desc_clean = re.sub(r'\s+', ' ', desc_lower)
        desc_clean = re.sub(r'[^a-zA-Z0-9\s]', '', desc_clean)
        return desc_clean
    except Exception as e:
        logger.warning(f"Error preprocessing description: {e}")
        return str(description).lower().strip()

# Load models on startup
def initialize():
    """Initialize models before first request"""
    if not load_models():
        logger.warning("Models not loaded. Some endpoints may not work.")

# Initialize models when module is imported
initialize()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    models_loaded = all([vectorizer, category_model, type_model])
    
    return jsonify({
        'status': 'healthy' if models_loaded else 'degraded',
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat()
    }), 200 if models_loaded else 503

# Root endpoint - serve frontend
@app.route('/')
def index():
    """Serve the main frontend page"""
    try:
        return send_from_directory('.', 'frontend.html')
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return jsonify({'error': 'Frontend file not found'}), 404

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    try:
        if filename in ['frontend.html', 'frontend.css', 'frontend.js']:
            return send_from_directory('.', filename)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        # Get description from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request body'
            }), 400
        
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Please enter a transaction description'
            }), 400
        
        # Check if models are loaded
        if not all([vectorizer, category_model, type_model]):
            logger.error("Models not loaded")
            return jsonify({
                'success': False,
                'error': 'Models not loaded. Please check server configuration.'
            }), 503
        
        # Preprocess description
        desc_processed = preprocess_description(description)
        
        # Vectorize
        X = vectorizer.transform([desc_processed])
        
        # Predict
        category = category_model.predict(X).item()
        trans_type = type_model.predict(X).item()
        
        # Extract amount
        amount = extract_amount(description)
        
        # Log prediction (optional, for monitoring)
        logger.info(f"Prediction: {category}, {trans_type}, Amount: {amount}")
        
        # Return results
        return jsonify({
            'success': True,
            'category': category,
            'transaction_type': trans_type,
            'amount': amount if amount else None,
            'description': description
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

if __name__ == '__main__':
    # Load models before starting server
    if not load_models():
        logger.warning("⚠️  Starting server without models. Some features may not work.")
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    logger.info(f"📝 Debug mode: {debug}")
    
    app.run(debug=debug, host=host, port=port)
