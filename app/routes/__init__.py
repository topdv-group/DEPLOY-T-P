# Routes package
from app.routes.employee_routes import employee_bp
from app.routes.attendance_routes import attendance_bp
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.payment_routes import payment_bp

__all__ = ['employee_bp', 'attendance_bp', 'admin_bp', 'auth_bp', 'payment_bp']