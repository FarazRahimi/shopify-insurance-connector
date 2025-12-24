import hmac
import hashlib
import json
import sqlite3
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Placeholder for Shopify webhook secret
WEBHOOK_SECRET = "your_shopify_webhook_secret_here"

# Database file path
DATABASE = "insurance_manifests.db"


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create the insurance_manifests table if it does not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_manifests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                email TEXT,
                total_price REAL,
                currency TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        print("Table insurance_manifests ready")
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {str(e)}")


def verify_webhook(data, hmac_header):
    """
    Verify Shopify webhook using HMAC SHA256.
    
    Args:
        data: Raw request data (bytes)
        hmac_header: X-Shopify-Hmac-Sha256 header value
        
    Returns:
        bool: True if verification succeeds, False otherwise
    """
    if not hmac_header:
        return False
    
    # Compute HMAC SHA256
    calculated_hmac = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()
    
    # Compare with header value using secure comparison
    return hmac.compare_digest(calculated_hmac, hmac_header)


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200


@app.route('/webhook/orders/create', methods=['POST'])
def webhook_orders_create():
    """
    Handle Shopify order creation webhook.
    
    Expected headers:
        X-Shopify-Hmac-Sha256: HMAC signature for verification
        
    Expected payload:
        JSON object containing order data
    """
    # Get HMAC header
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    
    # Get raw request data for verification
    raw_data = request.get_data()
    
    # Verify webhook
    if not verify_webhook(raw_data, hmac_header):
        return jsonify({"error": "Webhook verification failed"}), 401
    
    # Parse JSON payload
    try:
        order_data = request.get_json()
        
        if not order_data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Extract required fields
        order_id = order_data.get('id')
        total_price = order_data.get('total_price')
        currency = order_data.get('currency')
        
        # Extract customer email (may be nested in customer object)
        customer = order_data.get('customer', {})
        customer_email = customer.get('email') if isinstance(customer, dict) else None
        
        # If customer email is not in customer object, check top level
        if not customer_email:
            customer_email = order_data.get('email')
        
        # Convert order_id to string if it's not None
        if order_id is not None:
            order_id = str(order_id)
        
        # Convert total_price to float if it's a string
        if total_price is not None:
            try:
                total_price = float(total_price)
            except (ValueError, TypeError):
                total_price = None
        
        # Log received data in structured format
        print("=" * 60)
        print("Shopify Order Webhook Received")
        print("-" * 60)
        print(f"Order ID: {order_id}")
        print(f"Total Price: {total_price}")
        print(f"Currency: {currency}")
        print(f"Customer Email: {customer_email}")
        print("-" * 60)
        
        # Insert data into database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO insurance_manifests (order_id, email, total_price, currency, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, customer_email, total_price, currency, datetime.datetime.now()))
            
            conn.commit()
            inserted_id = cursor.lastrowid
            conn.close()
            
            print(f"Order saved to database with ID: {inserted_id}")
            print("=" * 60)
            
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            print("=" * 60)
            return jsonify({"error": "Failed to save order to database"}), 500
        
        # Return success response
        return jsonify({
            "status": "success",
            "message": "Webhook received and processed",
            "database_id": inserted_id
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
