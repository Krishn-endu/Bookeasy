const API_URL = 'http://localhost:5000/api';

class ApiService {
    static async login(email, password) {
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message);
            }
            return data;
        } catch (error) {
            throw error;
        }
    }

    static async getServices(token) {
        try {
            const response = await fetch(`${API_URL}/services`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            return await response.json();
        } catch (error) {
            throw error;
        }
    }
}
