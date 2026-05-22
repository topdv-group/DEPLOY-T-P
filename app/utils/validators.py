# app/utils/validators.py
def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return False
    clean = ''.join(filter(str.isdigit, str(phone)))
    return len(clean) >= 9

def validate_name(name):
    """Validate name"""
    if not name:
        return False
    return len(name.strip()) >= 2

def validate_rfid(rfid):
    """Validate RFID"""
    if not rfid:
        return False
    return len(str(rfid).strip()) > 0