#this is specifically for pawa pay

# app/webhook_routes.py - Separate webhook routes (NO prefix)
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger

# Create blueprint WITHOUT any url_prefix
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/pawapay/webhook', methods=['POST'])
def handle_webhook():
    """Handle PawaPay webhook at /pawapay/webhook (no /api prefix)"""
    try:
        # Log the request
        logger.info(f"Webhook received at path: {request.path}")
        logger.info(f"Webhook headers: {dict(request.headers)}")
        
        data = request.get_json()
        logger.info(f"Webhook data: {data}")
        
        payout_id = data.get("payoutId")
        status = data.get("status")
        
        if not payout_id:
            logger.error("Webhook missing payoutId")
            return jsonify({"error": "Missing payoutId"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        # Find employee by payout ID
        employee_id, employee_details = firebase_service.get_employees_by_payout_id(payout_id)
        
        if employee_id:
            update_data = {
                "payment_status": status,
                "webhook_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "webhook_received": True,
                "webhook_data": data
            }
            
            if status == "COMPLETED":
                update_data["paid"] = True
                logger.info(f"✅ Payment CONFIRMED via webhook for {employee_id}")
            elif status in ["FAILED", "REJECTED", "EXPIRED"]:
                update_data["paid"] = False
                logger.warning(f"❌ Payment FAILED via webhook for {employee_id}: {status}")
            
            firebase_service.update_employee(employee_id, update_data)
            return jsonify({"success": True, "message": "Webhook processed"}), 200
        else:
            logger.warning(f"Webhook received for unknown payoutId: {payout_id}")
            # Store for manual review
            unknown_ref = firebase_service.get_reference("UNKNOWN_WEBHOOKS")
            unknown_ref.push({
                "payout_id": payout_id,
                "status": status,
                "data": data,
                "received_at": datetime.now().isoformat()
            })
            return jsonify({"success": True, "message": "Webhook stored for review"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500