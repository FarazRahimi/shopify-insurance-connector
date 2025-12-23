import hmac
import hashlib
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Placeholder for Shopify webhook secret
WEBHOOK_SECRET = "your_shopify_webhook_secret_here"


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
        
        # Log received data in structured format
        print("=" * 60)
        print("Shopify Order Webhook Received")
        print("-" * 60)
        print(f"Order ID: {order_id}")
        print(f"Total Price: {total_price}")
        print(f"Currency: {currency}")
        print(f"Customer Email: {customer_email}")
        print("=" * 60)
        
        # Return success response
        return jsonify({
            "status": "success",
            "message": "Webhook received and processed"
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

