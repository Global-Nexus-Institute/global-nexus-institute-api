import paypalrestsdk
from flask import Blueprint, request, jsonify
from config import Config
import requests 
import json

payments_blueprint = Blueprint('payments', __name__)
paypalrestsdk.configure({
    "mode": "sandbox",  # Or "live"
    "client_id": Config.PAYPAL_CLIENT_ID,
    "client_secret": Config.PAYPAL_SECRET,
})

paypalAPI = Config.PAYPAL_API_BASE
paypalClient = Config.PAYPAL_CLIENT_ID
paypalSecret = Config.PAYPAL_SECRET

@payments_blueprint.route('/create-payment', methods=['POST'])
def create_payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": "10.00", "currency": "USD"},
            "description": "Purchase course"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:3000/courses/success",
            "cancel_url": "http://localhost:3000/cancel"
        }
    })

    if payment.create():
        return jsonify({"paymentID": payment.id}), 200
    else:
        return jsonify({"error": payment.error}), 400

@payments_blueprint.route('/execute-payment', methods=['POST'])
def execute_payment():
    payment_id = request.json.get('paymentID')
    payer_id = request.json.get('payerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return jsonify({"status": "Payment success"}), 200
    else:
        return jsonify({"error": payment.error}), 400
    
@payments_blueprint.route('/verify-payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    order_id = data.get("orderID")

    if not order_id:
        return jsonify({"success": False, "error": "No order ID provided."}), 400

    # Get the PayPal access token
    access_token = paypalrestsdk.Api().token
    
    # Verify the order with PayPal
    order_url = f"{paypalAPI}/v2/checkout/orders/{order_id}"
    response = request.get(order_url, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    })

    order_data = response.json()

    if order_data["status"] == "COMPLETED":
        # Handle successful payment, e.g., update the database
        return jsonify({"success": True, "message": "Payment verified successfully."}), 200
    else:
        return jsonify({"success": False, "message": "Payment verification failed."}), 400
    
def get_access_token():
    response = requests.post(f"{paypalAPI}/v1/oauth2/token", 
                             headers={"Accept": "application/json"}, 
                             data={ "grant_type": "client_credentials"},
                             auth=(paypalClient, paypalSecret))
    
    return response.json().get('access_token')

@payments_blueprint.route('/place-porder', methods=['POST'])
def create_order():
    access_token = get_access_token()

    headers  = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": request.json['amount']
            }
        }]
    }
    response = requests.post(f"{paypalAPI}/v2/checkout/orders", 
                             headers=headers, 
                             data=json.dumps(order_data))
    
    if response.status_code !=201:
        return jsonify({"error": "Error creating PayPal order", "details": response.json()}), 400
    
    return jsonify(response.json())

@payments_blueprint.route('/capture-payment', methods=['POST'])
def capture_payment():
    access_token = get_access_token()
    order_id = request.json['orderID']
    headers  = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{paypalAPI}/v2/checkout/orders/{order_id}/capture", 
                             headers=headers)
    return jsonify(response.json())

@payments_blueprint.route('/pay', methods=['POST'])
def pay():
    order = request.get_json()
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": f"http://localhost:3000/courses/{order.get('slug')}?success",
            "cancel_url": f"http://localhost:3000/courses/{order.get('slug')}?cancel"
        },
        "transactions": [{
            "amount": {"total": order.get("amount"), "currency": "USD"},
            "description": order.get("name")
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                token = approval_url.split("token=")[1]
                return jsonify({"token": token})
    else:
        return jsonify({"error": payment.error}), 500