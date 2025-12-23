from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import os
import logging

# Configure logging to look professional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# START CONFIGURATION
# In a real production app, these would be environment variables
API_KEY = "your_shopify_api_key"
API_SECRET = "your_shopify_shared_secret"
# END CONFIGURATION

def verify_webhook(data, hmac_header):
    # This verifies the signal actually came from Shopify
    digest = hmac.new(API_SECRET.encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed_hmac, hmac_header)

@app.route('/webhook/orders/create', methods=['POST'])
def order_created():
    logging.info("WEBHOOK RECEIVED: Order Creation Event")
    
    # 1. Get the data
    data = request.json
    
    # 2. Parse critical info for insurance
    order_id = data.get('id')
    total_price = data.get('total_price')
    currency = data.get('currency')
    customer = data.get('customer', {})
    email = customer.get('email')
    
    # 3. Log it (Simulating database entry)
    print("------------------------------------------------")
    print(f"PROCESSING ORDER ID: {order_id}")
    print(f"TRANSACTION VALUE: {total_price} {currency}")
    print(f"CUSTOMER EMAIL: {email}")
    print("STATUS: Queued for Insurance Manifest")
    print("------------------------------------------------")

    return jsonify({"status": "success"}), 200

@app.route('/', methods=['GET'])
def health_check():
    # Simple check to see if server is running
    return "Vertex Insurance Connector is Running...", 200

if __name__ == '__main__':
    logging.info("Server starting on port 5000...")
    app.run(port=5000)