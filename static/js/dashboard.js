// Performance Dashboard Main JavaScript

class PerformanceDashboard {
    constructor() {
        this.data = [];
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.setupFileUpload();
        this.updateMetrics();
        this.renderCharts();
        this.renderResultsTable();
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');
        const statusMessage = document.getElementById('statusMessage');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }

    async handleFileUpload(file) {
        const uploadStatus = document.getElementById('uploadStatus');
        const statusMessage = document.getElementById('statusMessage');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.txt')) {
            this.showUploadStatus('error', 'Please upload a CSV file.');
            return;
        }

        // Show upload status
        uploadStatus.style.display = 'block';
        progressBar.style.display = 'block';
        this.showUploadStatus('info', 'Uploading file...');

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += 10;
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
    }

    showUploadStatus(type, message) {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
    }

    async loadData() {
        try {
            // Load data from Flask API
            const response = await fetch('/api/data');
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.data = result.data;
                } else {
                    throw new Error(result.error || 'Failed to load data');
                }
            } else {
                // Fallback to sample data if API is not available
                console.warn('API not available, using sample data');
                this.data = this.generateSampleData();
            }
        } catch (error) {
            console.warn('Could not load data from API, using sample data:', error);
            this.data = this.generateSampleData();
        }
    }

    parseCSV(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',');
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
                const values = lines[i].split(',');
                const row = {};
                headers.forEach((header, index) => {
                    row[header.trim()] = values[index]?.trim();
                });
                data.push(row);
            }
        }
        return data;
    }

    generateSampleData() {
        // Generate sample performance data
        const data = [];
        const testNames = ['API Response', 'Database Query', 'Page Load', 'File Upload', 'Login Process'];
        
        for (let i = 0; i < 50; i++) {
            const date = new Date();
            date.setDate(date.getDate() - Math.floor(Math.random() * 30));
            
            data.push({
                timestamp: date.toISOString().split('T')[0],
                test_name: testNames[Math.floor(Math.random() * testNames.length)],
                response_time: Math.floor(Math.random() * 2000) + 100,
                status: Math.random() > 0.1 ? 'Success' : 'Failed',
                error_rate: Math.floor(Math.random() * 15)
            });
        }
        return data;
    }

    updateMetrics() {
        const totalTests = this.data.length;
        const avgResponseTime = this.data.reduce((sum, item) => sum + parseInt(item.response_time || 0), 0) / totalTests;
        const successRate = (this.data.filter(item => item.status === 'Success').length / totalTests) * 100;

        document.getElementById('total-performance').textContent = totalTests;
        document.getElementById('avg-response-time').textContent = `${Math.round(avgResponseTime)}ms`;
        document.getElementById('success-rate').textContent = `${Math.round(successRate)}%`;
    }

    renderResultsTable() {
        const tableBody = document.getElementById('resultsTableBody');
        tableBody.innerHTML = '';

        this.data.slice(0, 20).forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.timestamp}</td>
                <td>${row.test_name}</td>
                <td>${row.response_time}ms</td>
                <td><span class="status ${row.status.toLowerCase()}">${row.status}</span></td>
                <td>${row.error_rate}%</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    setupEventListeners() {
        const filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.filterResults());
        }

        // Smooth scrolling for navigation
        document.querySelectorAll('nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    filterResults() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        let filteredData = this.data;

        if (startDate) {
            filteredData = filteredData.filter(item => item.timestamp >= startDate);
        }
        if (endDate) {
            filteredData = filteredData.filter(item => item.timestamp <= endDate);
        }

        // Update table with filtered data
        const tableBody = document.getElementById('resultsTableBody');
        tableBody.innerHTML = '';

        filteredData.slice(0, 20).forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.timestamp}</td>
                <td>${row.test_name}</td>
                <td>${row.response_time}ms</td>
                <td><span class="status ${row.status.toLowerCase()}">${row.status}</span></td>
                <td>${row.error_rate}%</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    renderCharts() {
        // Initialize charts after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.createPerformanceChart();
            this.createResponseTimeChart();
            this.createErrorRateChart();
        }, 100);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new PerformanceDashboard();
});

// Add some utility functions
window.formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
};

window.formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
};
