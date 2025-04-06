document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');

    try {
        const response = await ApiService.login(email, password);
        messageDiv.textContent = 'Login successful!';
        messageDiv.style.backgroundColor = '#dff0d8';
        
        // Store token in localStorage
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        // Redirect or update UI as needed
        window.location.href = '/dashboard.html';
    } catch (error) {
        messageDiv.textContent = error.message;
        messageDiv.style.backgroundColor = '#f2dede';
    }
});
