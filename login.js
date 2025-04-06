const CONFIG = {
    API_URL: 'http://localhost:5000/login',
    REDIRECT_DELAY: 2000,
    REDIRECT_URL: '/dashboard.html'
};

function showMessage(element, message, type) {
    element.textContent = message;
    element.style.display = 'block';
    element.className = `message ${type}`;
}

function setLoading(isLoading) {
    const button = document.querySelector('button[type="submit"]');
    button.disabled = isLoading;
    button.innerHTML = isLoading ? '<span class="spinner"></span> Loading...' : 'Login';
}

function validateForm(email, password) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Please enter a valid email';
    if (password.length < 6) return 'Password must be at least 6 characters';
    return null;
}

let isSubmitting = false;
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    
    if (isSubmitting) return;
    isSubmitting = true;

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');
    
    const validationError = validateForm(email, password);
    if (validationError) {
        showMessage(messageDiv, validationError, 'error');
        isSubmitting = false;
        return;
    }

    try {
        setLoading(true);
        const res = await fetch(CONFIG.API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
  
        const data = await res.json();
        showMessage(messageDiv, data.message, res.ok ? 'success' : 'error');

        if (res.ok) {
            this.reset();
            sessionStorage.setItem('userEmail', email);
            setTimeout(() => {
                window.location.href = CONFIG.REDIRECT_URL;
            }, CONFIG.REDIRECT_DELAY);
        }
    } catch (error) {
        showMessage(messageDiv, 'Connection error. Please try again.', 'error');
    } finally {
        setLoading(false);
        isSubmitting = false;
    }
});
