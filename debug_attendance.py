# debug_payment.py
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_json:
    if firebase_json.startswith("'") and firebase_json.endswith("'"):
        firebase_json = firebase_json[1:-1]
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH"))

database_url = os.getenv("DATABASE_URL")
firebase_admin.initialize_app(cred, {'databaseURL': database_url})

# Get settings
settings_ref = db.reference("SYSTEM_SETTINGS")
settings = settings_ref.get()

# Get employees
employees_ref = db.reference("EMPLOYEES")
employees = employees_ref.get()

today = datetime.now().strftime("%Y-%m-%d")
current_time = datetime.now().strftime("%H:%M")
payment_time = settings.get("paymentTime", "17:30")
pay_amount = settings.get("payAmount", 100)
api_key = os.getenv("PAWAPAY_API_KEY")

print("=" * 60)
print("PAYMENT SYSTEM DIAGNOSTIC")
print("=" * 60)
print(f"Current time: {current_time}")
print(f"Payment time setting: {payment_time}")
print(f"Time reached: {current_time >= payment_time}")
print(f"Pay amount: {pay_amount} RWF")
print(f"PawaPay API Key configured: {'✅ YES' if api_key else '❌ NO'}")
print(f"API URL: {settings.get('pawapayApiUrl', 'Not set')}")
print("=" * 60)

# Check employees
attended_count = 0
paid_count = 0
pending_count = 0

print("\nEmployees today:")
print("-" * 60)

for key, details in employees.items():
    name = details.get("name", "Unknown")
    attended = details.get("attended", False)
    paid = details.get("paid", False)
    payment_status = details.get("payment_status", "N/A")
    
    if attended:
        attended_count += 1
        if paid:
            paid_count += 1
        elif payment_status == "PENDING":
            pending_count += 1
            print(f"  {name}: Attended ✅ | Payment PENDING ⏳ (payout_id: {details.get('payoutId', 'N/A')[:20]}...)")
        else:
            print(f"  {name}: Attended ✅ | Not paid ❌ | Status: {payment_status}")
    else:
        print(f"  {name}: Absent ❌")

print("-" * 60)
print(f"Summary:")
print(f"  Attended today: {attended_count}")
print(f"  Paid today: {paid_count}")
print(f"  Pending payments: {pending_count}")
print(f"  Ready to pay: {attended_count - paid_count - pending_count}")
print("=" * 60)

# Check if payment should trigger
if current_time >= payment_time:
    print(f"\n⚠️ PAYMENT TIME HAS BEEN REACHED!")
    print(f"   The payment timer should have triggered.")
    print(f"   Check your logs for: 'Starting employee payment requests...'")
else:
    print(f"\n⏳ Payment time not reached yet.")
    print(f"   Will trigger at {payment_time}")