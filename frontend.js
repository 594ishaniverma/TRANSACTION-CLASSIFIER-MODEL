// API endpoint - change this if your Flask app runs on a different port
const API_URL = 'http://localhost:5000/predict';

// Function to handle prediction
async function predictTransaction() {
    const description = document.getElementById('description').value.trim();
    const predictBtn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const resultsSection = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    
    // Validate input
    if (!description) {
        showError('Please enter a transaction description');
        return;
    }
    
    // Show loading state
    predictBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    resultsSection.style.display = 'none';
    errorDiv.style.display = 'none';
    
    try {
        // Send request to Flask backend
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description: description
            })
        });
        
        const data = await response.json();
        
        // Hide loading state
        predictBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        
        // Check for errors
        if (!response.ok || data.error) {
            showError(data.error || 'Something went wrong. Please try again.');
            return;
        }
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        // Hide loading state
        predictBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        
        showError('Failed to connect to server. Make sure Flask app is running on port 5000.');
        console.error('Error:', error);
    }
}

// Function to display results
function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    
    // Hide error if visible
    errorDiv.style.display = 'none';
    
    // Update result fields
    document.getElementById('resultDescription').textContent = data.description || '-';
    document.getElementById('resultCategory').textContent = data.category || '-';
    
    // Update transaction type with color coding
    const typeElement = document.getElementById('resultType');
    const transType = data.transaction_type || '-';
    typeElement.textContent = transType;
    
    // Remove old classes
    typeElement.classList.remove('type-credited', 'type-debited');
    
    // Add appropriate class based on type
    if (transType.toLowerCase() === 'credited') {
        typeElement.classList.add('type-credited');
    } else if (transType.toLowerCase() === 'debited') {
        typeElement.classList.add('type-debited');
    }
    
    // Update amount
    const amountElement = document.getElementById('resultAmount');
    if (data.amount !== null && data.amount !== undefined && data.amount > 0) {
        amountElement.textContent = `₹${data.amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        amountElement.style.color = '#10b981'; // Green color for amount
        amountElement.style.fontWeight = '700';
    } else {
        amountElement.textContent = 'Not found in description';
        amountElement.style.color = '#999';
        amountElement.style.fontWeight = '500';
    }
    
    // Show results section
    resultsSection.style.display = 'block';
}

// Function to show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Allow Enter key to trigger prediction (Ctrl+Enter or Cmd+Enter)
document.getElementById('description').addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        predictTransaction();
    }
});

