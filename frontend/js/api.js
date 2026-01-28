const API_URL = 'http://127.0.0.1:8000';

// API Client
const api = {
    // Get auth token
    getToken() {
        return localStorage.getItem('token');
    },

    // Get headers with auth
    getHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    },

    // Register
    async register(email, password) {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return response.json();
    },

    // Login
    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email);  // OAuth2 uses 'username' field
        formData.append('password', password);

        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        return response.json();
    },

    // Get current user
    async getMe() {
        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get user info');
        return response.json();
    },

    // Upload transactions
    async uploadTransactions(file) {
        const formData = new FormData();
        formData.append('file', file);

        const token = this.getToken();
        const response = await fetch(`${API_URL}/api/transactions/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    },

    // Get transactions
    async getTransactions() {
        const response = await fetch(`${API_URL}/api/transactions`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get transactions');
        return response.json();
    },

    // Get stats
    async getStats() {
        const response = await fetch(`${API_URL}/api/transactions/stats`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get stats');
        return response.json();
    },

    // Get subscriptions
    async getSubscriptions() {
        const response = await fetch(`${API_URL}/api/subscriptions`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get subscriptions');
        return response.json();
    },

    // Get forecast
    async getForecast() {
        const response = await fetch(`${API_URL}/api/transactions/forecast`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get forecast');
        return response.json();
    },

    // Get notifications
    async getNotifications() {
        const response = await fetch(`${API_URL}/api/subscriptions/notifications`, {
            headers: this.getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get notifications');
        return response.json();
    },

    // Update subscription
    async updateSubscription(id, status) {
        const response = await fetch(`${API_URL}/api/subscriptions/${id}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify({ status })
        });

        if (!response.ok) throw new Error('Failed to update subscription');
        return response.json();
    }
};
