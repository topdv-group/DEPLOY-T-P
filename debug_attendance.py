# mark_attended.py
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

load_dotenv()

# Initialize Firebase
key_path = os.getenv("FIREBASE_KEY_PATH", "serviceAccountKey.json")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('DATABASE_URL')
})

# Get all employees
employees_ref = db.reference("EMPLOYEES")
employees = employees_ref.get()

if not employees:
    print("No employees found! Create one first.")
    # Create a test employee
    test_employee = {
        "name": "Test Employee",
        "phone": "0788888888",
        "rfid": "TEST123",
        "attended": True,
        "paid": False,
        "attendance": [{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }],
        "registerTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    new_ref = employees_ref.push(test_employee)
    print(f"✅ Created test employee: Test Employee (RFID: TEST123)")
else:
    # Mark first employee as attended
    for key, details in employees.items():
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Add attendance record
        attendance_list = details.get("attendance", [])
        attendance_list.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": current_date
        })
        
        # Update employee
        employees_ref.child(key).update({
            "attended": True,
            "attendance": attendance_list,
            "last_attendance": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_attendance_date": current_date
        })
        print(f"✅ Marked {details.get('name')} as attended")
        break

print("\nNow run payments with: curl -X POST http://localhost:5000/api/admin/payments/trigger")