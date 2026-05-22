// auth.js - Authentication functions

// Check if user is authenticated
async function checkAuth() {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        redirectToLogin();
        return false;
    }
    
    try {
        const response = await fetch('/api/auth/verify', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const result = await response.json();
        
        if (!result.valid) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            redirectToLogin();
            return false;
        }
        
        // Update UI with user info
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail && document.getElementById('userEmail')) {
            document.getElementById('userEmail').textContent = userEmail;
        }
        
        return true;
    } catch (error) {
        console.error('Auth check error:', error);
        redirectToLogin();
        return false;
    }
}

// Redirect to login page
function redirectToLogin() {
    const currentPath = window.location.pathname;
    // Don't redirect if already on login pages
    if (!currentPath.includes('login.html') && 
        !currentPath.includes('forgot-password.html') &&
        !currentPath.includes('reset-password.html')) {
        window.location.href = '/login.html';
    }
}

// Login function
async function login(email, password, rememberMe = false) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, rememberMe })
        });
        
        const result = await response.json();
        
        if (result.success) {
            localStorage.setItem('authToken', result.token);
            localStorage.setItem('userEmail', result.email);
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
            }
            window.location.href = '/';
            return true;
        } else {
            showNotification(result.error || 'Login failed', 'error');
            return false;
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Login failed. Please try again.', 'error');
        return false;
    }
}

// Logout function
async function logout() {
    const token = localStorage.getItem('authToken');
    
    if (token) {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('rememberMe');
    
    window.location.href = '/login.html';
}

// Get auth headers for API calls
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Add logout button to all pages
function addLogoutButton() {
    const headerActions = document.querySelector('.header-actions');
    if (headerActions && !document.getElementById('logoutBtn')) {
        const logoutBtn = document.createElement('button');
        logoutBtn.id = 'logoutBtn';
        logoutBtn.className = 'btn-secondary';
        logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Logout';
        logoutBtn.onclick = logout;
        headerActions.appendChild(logoutBtn);
    }
}

// Run auth check on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Skip auth check for login pages
    const skipPaths = ['login.html', 'forgot-password.html', 'reset-password.html'];
    const currentPath = window.location.pathname;
    
    if (!skipPaths.some(path => currentPath.includes(path))) {
        const isAuth = await checkAuth();
        if (isAuth) {
            addLogoutButton();
        }
    }
});