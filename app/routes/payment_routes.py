# app/routes/payment_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.utils.logger import logger

payment_bp = Blueprint('payment', __name__, url_prefix='/api')

@payment_bp.route("/pawapay/webhook", methods=["POST"])
def pawapay_webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        payout_id = data.get("payoutId")
        status = data.get("status")
        
        if not payout_id:
            return jsonify({"error": "Missing payoutId"}), 400
        
        firebase_service = current_app.config['FIREBASE_SERVICE']
        
        employee_id, employee_details = firebase_service.get_employees_by_payout_id(payout_id)
        
        if employee_id:
            firebase_service.update_employee(employee_id, {
                "payment_status": status,
                "webhook_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "webhook_data": data
            })
            
            if status == "COMPLETED":
                firebase_service.update_employee(employee_id, {"paid": True})
                logger.info(f"Payment CONFIRMED for employee {employee_id}")
            elif status in ["FAILED", "REJECTED", "EXPIRED"]:
                firebase_service.update_employee(employee_id, {"paid": False})
                logger.warning(f"Payment FAILED for employee {employee_id}: {status}")
        else:
            logger.warning(f"Webhook received for unknown payoutId: {payout_id}")
        
        return jsonify({"success": True, "message": "Webhook processed"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ADD THIS NEW ENDPOINT ↓↓↓
@payment_bp.route('/admin/payments/trigger', methods=['POST'])
def force_payment():
    import requests
    import uuid
    from datetime import datetime
    
    firebase_service = current_app.config['FIREBASE_SERVICE']
    settings_service = current_app.config['SETTINGS_SERVICE']
    
    # Get employee who attended
    employees = firebase_service.get_employees()
    target_employee = None
    
    for key, emp in employees.items():
        if emp.get('attended') and not emp.get('paid'):
            target_employee = (key, emp)
            break
    
    if not target_employee:
        return jsonify({"error": "No unpaid attended employee"}), 400
    
    emp_id, emp_data = target_employee
    phone = emp_data.get('phone')
    pay_amount = settings_service.get_setting("payAmount", 100)
    api_key = os.getenv("PAWAPAY_API_KEY")
    api_url = settings_service.get_setting("pawapayApiUrl")
    
    # Format phone
    clean = ''.join(filter(str.isdigit, phone))
    if not clean.startswith('250'):
        clean = '250' + clean[-9:]
    
    payout_id = str(uuid.uuid4())
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "payoutId": payout_id,
        "amount": pay_amount,
        "currency": "RWF",
        "recipient": {
            "type": "MMO",
            "accountDetails": {"phoneNumber": clean, "provider": "MTN_MOMO_RWA"}
        }
    }
    
    # Send to PawaPay
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    result = response.json()
    
    if response.status_code in [200, 201, 202]:
        firebase_service.update_employee(emp_id, {
            "payoutId": payout_id,
            "payment_status": "PENDING",
            "paid": False
        })
        return jsonify({"success": True, "message": "Payment sent", "payoutId": payout_id}), 200
    else:
        return jsonify({"success": False, "error": result}), 400
