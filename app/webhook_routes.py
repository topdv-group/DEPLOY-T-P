# app/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger

# Create blueprint with NO prefix (so it's at /pawapay/webhook, not /api/pawapay/webhook)
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/pawapay/webhook', methods=['POST', 'GET'])
def handle_webhook():
    """Handle PawaPay webhook"""
    if request.method == 'GET':
        return jsonify({
            "status": "webhook endpoint is working",
            "message": "Send POST requests here for payment confirmations"
        }), 200
    
    # POST request - process webhook
    try:
        logger.info(f"Webhook received")
        
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received")
            return jsonify({"error": "No JSON data"}), 400
        
        logger.info(f"Webhook data: {data}")
        
        payout_id = data.get("payoutId")
        status = data.get("status")
        
        if not payout_id:
            logger.error("Missing payoutId in webhook")
            return jsonify({"error": "Missing payoutId"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        # Find employee by payout ID
        employees = firebase_service.get_employees()
        employee_found = False
        
        if employees:
            for key, details in employees.items():
                if details.get("payoutId") == payout_id:
                    update_data = {
                        "payment_status": status,
                        "webhook_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    if status == "COMPLETED":
                        update_data["paid"] = True
                        logger.info(f"✅ Payment CONFIRMED for employee {key}")
                    elif status in ["FAILED", "REJECTED", "EXPIRED"]:
                        update_data["paid"] = False
                        logger.warning(f"❌ Payment FAILED for employee {key}: {status}")
                    else:
                        logger.info(f"Payment status updated to {status} for employee {key}")
                    
                    firebase_service.update_employee(key, update_data)
                    employee_found = True
                    break
        
        if employee_found:
            return jsonify({"success": True, "message": "Webhook processed"}), 200
        else:
            logger.warning(f"Payout ID not found in database: {payout_id}")
            return jsonify({"success": False, "message": "Payout ID not found"}), 404
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500