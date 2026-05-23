# fix_all_attendance.py
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

employees_ref = db.reference("EMPLOYEES")
employees = employees_ref.get()

today = datetime.now().strftime("%Y-%m-%d")
updated_count = 0

print(f"Fixing attendance for {today}")
print("=" * 60)

for key, details in employees.items():
    name = details.get("name", "Unknown")
    attendance_list = details.get("attendance", [])
    
    # Check if there's an attendance record for today
    attended_today = False
    for record in attendance_list:
        if record.get("date") == today:
            attended_today = True
            break
    
    current_attended = details.get("attended", False)
    
    if attended_today != current_attended:
        print(f"Fixing {name}: attended={current_attended} -> should be {attended_today}")
        employees_ref.child(key).update({"attended": attended_today})
        updated_count += 1

print("=" * 60)
print(f"Fixed {updated_count} employees")
print("\n✅ All employees are now consistent!")