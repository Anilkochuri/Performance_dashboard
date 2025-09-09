// Dashboard with Login JavaScript Enhancement

// Load user info when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
});

// Load user information
async function loadUserInfo() {
    try {
        const response = await fetch('/api/user-info');
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                document.getElementById('username').textContent = result.username;
            }
        }
    } catch (error) {
        console.log('Could not load user info:', error);
    }
}

// Enhance existing dashboard functionality
if (window.dashboard) {
    // Override the existing loadData method to include user context
    const originalLoadData = window.dashboard.loadData;
    window.dashboard.loadData = async function() {
        try {
            const response = await fetch('/api/data');
            if (response.status === 401) {
                // Redirect to login if not authenticated
                window.location.href = '/login';
                return;
            }
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.data = result.data;
                    console.log(`Data loaded for user: ${result.user || 'unknown'}`);
                } else {
                    throw new Error(result.error || 'Failed to load data');
                }
            } else {
                throw new Error('Failed to fetch data');
            }
        } catch (error) {
            console.warn('Could not load data from API:', error);
            // Fallback to sample data if available
            if (this.generateSampleData) {
                this.data = this.generateSampleData();
            }
        }
    };

    // Override upload method to include user feedback
    const originalHandleFileUpload = window.dashboard.handleFileUpload;
    if (originalHandleFileUpload) {
        window.dashboard.handleFileUpload = async function(file) {
            const uploadStatus = document.getElementById('uploadStatus');
            const statusMessage = document.getElementById('statusMessage');
            const progressBar = document.querySelector('.progress-bar');
            const progressFill = document.querySelector('.progress-fill');

            if (!file) {
                this.showUploadStatus('error', '❌ Please select a file to upload');
                return;
            }

            if (!file.name.toLowerCase().endsWith('.csv')) {
                this.showUploadStatus('error', '❌ Please upload a CSV file');
                return;
            }

            try {
                uploadStatus.style.display = 'block';
                progressBar.style.display = 'block';
                this.showUploadStatus('info', '📤 Uploading file...');

                const formData = new FormData();
                formData.append('file', file);

                // Simulate progress
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressFill.style.width = progress + '%';
                    
                    if (progress >= 90) {
                        clearInterval(progressInterval);
                    }
                }, 100);

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                clearInterval(progressInterval);
                progressFill.style.width = '100%';

                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                const result = await response.json();

                if (result.success) {
                    this.showUploadStatus('success', `✅ ${result.message}`);
                    
                    // Reload dashboard data
                    await this.loadData();
                    this.updateMetrics();
                    this.renderCharts();
                    this.renderResultsTable();
                    
                    setTimeout(() => {
                        uploadStatus.style.display = 'none';
                        progressBar.style.display = 'none';
                        progressFill.style.width = '0%';
                    }, 3000);
                } else {
                    this.showUploadStatus('error', `❌ ${result.error}`);
                }
            } catch (error) {
                this.showUploadStatus('error', `❌ Upload failed: ${error.message}`);
            }
        };
    }
}

// Add logout confirmation
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('logout-btn') || e.target.closest('.logout-btn')) {
        e.preventDefault();
        if (confirm('Are you sure you want to logout?')) {
            window.location.href = '/logout';
        }
    }
});

// Add session timeout warning (optional)
let lastActivity = Date.now();
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

function updateActivity() {
    lastActivity = Date.now();
}

// Track user activity
document.addEventListener('click', updateActivity);
document.addEventListener('keypress', updateActivity);
document.addEventListener('scroll', updateActivity);

// Check for session timeout every minute
setInterval(() => {
    if (Date.now() - lastActivity > SESSION_TIMEOUT) {
        if (confirm('Your session has been inactive for 30 minutes. Do you want to continue?')) {
            updateActivity();
        } else {
            window.location.href = '/logout';
        }
    }
}, 60000);

console.log('🔐 Dashboard with authentication loaded successfully');
