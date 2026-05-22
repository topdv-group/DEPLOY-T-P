// config.js - API Configuration
const API_BASE_URL = ''; // Empty string means use same origin

// API endpoints - Note the /api prefix
const API_ENDPOINTS = {
    // Auth endpoints
    AUTH_LOGIN: '/api/auth/login',
    AUTH_VERIFY: '/api/auth/verify',
    AUTH_LOGOUT: '/api/auth/logout',
    AUTH_FORGOT_PASSWORD: '/api/auth/forgot-password',
    AUTH_RESET_PASSWORD: '/api/auth/reset-password',
    AUTH_CHANGE_PASSWORD: '/api/auth/change-password',
    
    // Employee endpoints
    REGISTER: '/api/register',
    GET_EMPLOYEES: '/api/get_employees',
    GET_EMPLOYEE: (id) => `/api/get_employee/${id}`,
    UPDATE_EMPLOYEE: (id) => `/api/update_employee/${id}`,
    DELETE_EMPLOYEE: (id) => `/api/delete_employee/${id}`,
    
    // Attendance endpoints
    MARK_ATTENDANCE: '/api/markAttendance',
    GET_ATTENDANCE: '/api/get_attendance',
    
    // Stats endpoint
    STATS: '/api/admin/stats',
    
    // Admin endpoints
    ADMIN_SETTINGS: '/api/admin/settings',
    ADMIN_SETTINGS_PAYMENT: '/api/admin/settings/payment',
    ADMIN_SETTINGS_RESET: '/api/admin/settings/reset',
    ADMIN_BACKUP: '/api/admin/backup',
    ADMIN_LOGS: '/api/admin/logs',
    ADMIN_SYSTEM_INFO: '/api/admin/system-info',
    
    // Payment endpoints
    WEBHOOK: '/api/pawapay/webhook'
};

// Helper function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`Making API call to: ${url}`, { method, data });
    
    // Get auth token if available
    const token = localStorage.getItem('authToken');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Add auth header if token exists
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        console.log(`API response from ${endpoint}:`, result);
        
        // Handle unauthorized
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            window.location.href = '/login.html';
            throw new Error('Session expired. Please login again.');
        }
        
        if (!response.ok) {
            throw new Error(result.error || result.message || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Utility functions
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Add styles dynamically
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                gap: 10px;
                z-index: 10000;
                animation: slideIn 0.3s ease;
                font-size: 14px;
                font-weight: 500;
            }
            .notification.success {
                border-left: 4px solid #10b981;
                color: #065f46;
            }
            .notification.error {
                border-left: 4px solid #ef4444;
                color: #991b1b;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(date = new Date()) {
    return date.toISOString().split('T')[0];
}

function formatDateTime(date = new Date()) {
    return date.toLocaleString('en-RW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function updateTimeDisplay() {
    const timeElement = document.getElementById('currentTime'); 
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString('en-RW');
    }
}

setInterval(updateTimeDisplay, 1000);
updateTimeDisplay();