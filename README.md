# Transaction Classifier

A Flask-based web application that classifies bank transaction descriptions into categories and transaction types using machine learning.

## Features
##project
- **Transaction Classification**: Automatically categorizes transactions (Food & Dining, Shopping, Bills & Utilities, etc.)
- **Transaction Type Detection**: Identifies if a transaction is credited or debited
- **Amount Extraction**: Extracts transaction amounts from descriptions
- **Simple Web Interface**: Clean, modern UI for easy interaction

## Requirements

- Python 3.8+
- Flask
- scikit-learn
- joblib
- Other dependencies listed in `requirements.txt`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure model files are present:
   - `tfidf_vectorizer.pkl`
   - `trained_model.pkl`
   - `transaction_type_model.pkl`

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Production Mode

Set environment variables:
```bash
export PORT=5000
export HOST=0.0.0.0
export DEBUG=False
python app.py
```

Or use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
```
GET /health
```
Returns server health status and model loading status.

### Prediction
```
POST /predict
Content-Type: application/json

{
  "description": "rs 5000 debited for zomato order"
}
```

Response:
```json
{
  "success": true,
  "category": "Food & Dining",
  "transaction_type": "debited",
  "amount": 5000.0,
  "description": "rs 5000 debited for zomato order"
}
```

## Project Structure

```
.
├── app.py                 # Flask application
├── frontend.html          # Frontend HTML
├── frontend.css           # Frontend styles
├── frontend.js            # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── trained_model.pkl      # Category prediction model
├── transaction_type_model.pkl  # Transaction type model
└── tfidf_vectorizer.pkl   # TF-IDF vectorizer
```

## Notes

- The application uses CORS to allow cross-origin requests
- Models are loaded at startup
- Health check endpoint available at `/health`
- Proper error handling and logging implemented

