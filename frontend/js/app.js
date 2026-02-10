// Check authentication
if (!api.getToken()) {
    window.location.href = 'login.html';
}

// State
let currentUser = null;

// Initialize app
async function init() {
    try {
        currentUser = await api.getMe();
        await loadDashboardData();
        setupEventListeners();
    } catch (error) {
        console.error('Initialization error:', error);
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Load stats
        const stats = await api.getStats();
        document.getElementById('totalTransactions').textContent = (stats.total_transactions || 0).toLocaleString();
        document.getElementById('totalSubscriptions').textContent = stats.total_subscriptions || 0;
        document.getElementById('monthlySubCost').textContent = `₹${Math.round(stats.monthly_subscription_cost || 0).toLocaleString('en-IN')}`;
        document.getElementById('avgSpentPerMonth').textContent = `₹${Math.round(stats.avg_spent_per_month || 0).toLocaleString('en-IN')}`;
        document.getElementById('totalSpentOverall').textContent = `₹${Math.round(stats.total_spent_overall || 0).toLocaleString('en-IN')}`;

        // Update Total Amount Spent stat specifically if needed
        const totalSpentOverallElem = document.getElementById('totalSpentOverall');
        if (totalSpentOverallElem.textContent === '₹NaN' || totalSpentOverallElem.textContent === '₹-') {
            totalSpentOverallElem.textContent = '₹0';
        }

        // Load subscriptions
        await loadSubscriptions();

        // Load forecast
        const forecast = await api.getForecast();
        createBalanceForecastChart(forecast);

        // Load notifications
        await loadNotifications();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load subscriptions
async function loadSubscriptions() {
    try {
        const subscriptions = await api.getSubscriptions();
        const container = document.getElementById('subscriptionsList');

        container.classList.remove('loading');

        if (subscriptions.length === 0) {
            container.innerHTML = '<p style="color: #94a3b8; text-align: center; width: 100%;">No subscriptions detected yet. Upload transactions to get started!</p>';
            return;
        }

        container.className = 'subscriptions-grid';
        container.innerHTML = subscriptions.map(sub => `
            <div class="subscription-item">
                <div class="subscription-info">
                    <h3>${sub.name}</h3>
                    <p>${sub.frequency} • ${(sub.confidence_score * 100).toFixed(0)}% confidence</p>
                </div>
                <div class="subscription-amount">₹${Math.round(sub.amount).toLocaleString('en-IN')}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading subscriptions:', error);
    }
}

// Load notifications
async function loadNotifications() {
    try {
        const notifications = await api.getNotifications();
        const container = document.getElementById('notificationsList');
        const badge = document.getElementById('notificationCount');

        if (notifications.length === 0) {
            container.innerHTML = '<p style="color: #94a3b8; text-align: center;">No notifications</p>';
            badge.style.display = 'none';
            return;
        }

        // Show unread count
        const unreadCount = notifications.filter(n => !n.read).length;
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'block';
        }

        container.innerHTML = notifications.map(notif => {
            const date = new Date(notif.created_at);
            const timeAgo = getTimeAgo(date);

            return `
                <div class="notification-item ${notif.type}">
                    <div class="notification-message">${notif.message}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Time ago helper
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' years ago';

    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' months ago';

    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' days ago';

    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' hours ago';

    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutes ago';

    return 'Just now';
}

// Event listeners
function setupEventListeners() {
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });

    // Notification bell
    document.getElementById('notificationBell').addEventListener('click', () => {
        document.getElementById('notificationsPanel').classList.add('open');
    });

    document.getElementById('closeNotifications').addEventListener('click', () => {
        document.getElementById('notificationsPanel').classList.remove('open');
    });

    // Clear data
    document.getElementById('clearDataBtn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear all transaction data? This action cannot be undone.')) {
            await handleClearData();
        }
    });

    // File upload
    const uploadSection = document.getElementById('uploadSection');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');

    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            await handleFileUpload(file);
        }
    });

    // Drag and drop
    uploadSection.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadSection.classList.add('dragover');
    });

    uploadSection.addEventListener('dragleave', () => {
        uploadSection.classList.remove('dragover');
    });

    uploadSection.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadSection.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            await handleFileUpload(file);
        } else {
            showUploadStatus('Please upload a CSV file', 'error');
        }
    });
}

// Handle file upload
async function handleFileUpload(file) {
    const statusDiv = document.getElementById('uploadStatus');

    try {
        showUploadStatus('Uploading and analyzing...', 'loading');

        const result = await api.uploadTransactions(file);

        showUploadStatus(`✅ Successfully processed ${result.transactions_count} transactions!`, 'success');

        // Reload dashboard data
        setTimeout(() => {
            loadDashboardData();
        }, 1000);
    } catch (error) {
        showUploadStatus(`❌ ${error.message}`, 'error');
    }
}

// Handle clear data
async function handleClearData() {
    try {
        console.log('Initiating hard clear...');

        // Immediate UI Wipe
        document.getElementById('totalTransactions').textContent = '0';
        document.getElementById('totalSubscriptions').textContent = '0';
        document.getElementById('monthlySubCost').textContent = '₹0';
        document.getElementById('avgSpentPerMonth').textContent = '₹0';
        document.getElementById('totalSpentOverall').textContent = '₹0';

        const subList = document.getElementById('subscriptionsList');
        if (subList) subList.innerHTML = '<p class="loading">Clearing data...</p>';

        if (typeof d3 !== 'undefined' && document.getElementById('balanceChart')) {
            d3.select('#balanceChart').selectAll('*').remove();
        }

        // Backend Call
        await api.deleteTransactions();

        // Reset file input
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.value = '';

        showUploadStatus('✅ All data wiped successfully!', 'success');

        // Final UI State
        if (subList) {
            subList.innerHTML = '<p style="color: #94a3b8; text-align: center; width: 100%;">Data cleared. Ready for new upload.</p>';
            subList.className = 'subscriptions-grid';
        }

        // Reload to be absolutely sure
        setTimeout(async () => {
            await loadDashboardData();
        }, 300);

    } catch (error) {
        console.error('Hard clear error:', error);
        showUploadStatus(`❌ Error: ${error.message}`, 'error');
    }
}

// Show upload status
function showUploadStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.style.color = type === 'error' ? '#ef4444' :
        type === 'success' ? '#10b981' : '#94a3b8';
}

// Initialize on load
init();
