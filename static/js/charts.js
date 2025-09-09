// Charts functionality for Performance Dashboard

class ChartManager {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.charts = {};
    }

    createPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        // Group data by date for time series
        const dateGroups = {};
        this.dashboard.data.forEach(item => {
            const date = item.timestamp;
            if (!dateGroups[date]) {
                dateGroups[date] = [];
            }
            dateGroups[date].push(parseInt(item.response_time || 0));
        });

        // Calculate average response time per date
        const labels = Object.keys(dateGroups).sort();
        const data = labels.map(date => {
            const times = dateGroups[date];
            return times.reduce((sum, time) => sum + time, 0) / times.length;
        });

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Response Time (ms)',
                    data: data,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Performance Trend Over Time'
                    }
                }
            }
        });
    }

    createResponseTimeChart() {
        const ctx = document.getElementById('responseTimeChart');
        if (!ctx) return;

        // Create histogram of response times
        const responseTimes = this.dashboard.data.map(item => parseInt(item.response_time || 0));
        const bins = this.createHistogramBins(responseTimes, 10);

        this.charts.responseTime = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bins.labels,
                datasets: [{
                    label: 'Number of Tests',
                    data: bins.data,
                    backgroundColor: 'rgba(245, 87, 108, 0.6)',
                    borderColor: 'rgba(245, 87, 108, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Tests'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Response Time Range (ms)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Response Time Distribution'
                    }
                }
            }
        });
    }

    createErrorRateChart() {
        const container = document.getElementById('errorRateChart');
        if (!container) return;

        // Group by test name and calculate error rates
        const testGroups = {};
        this.dashboard.data.forEach(item => {
            const testName = item.test_name;
            if (!testGroups[testName]) {
                testGroups[testName] = { total: 0, errors: 0 };
            }
            testGroups[testName].total++;
            if (item.status !== 'Success') {
                testGroups[testName].errors++;
            }
        });

        const labels = Object.keys(testGroups);
        const errorRates = labels.map(testName => {
            const group = testGroups[testName];
            return (group.errors / group.total) * 100;
        });

        const colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ];

        // Create pie chart using Plotly
        const data = [{
            values: errorRates,
            labels: labels,
            type: 'pie',
            marker: {
                colors: colors
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        }];

        const layout = {
            title: {
                text: 'Error Rate by Test Type',
                font: { size: 16 }
            },
            showlegend: true,
            margin: { t: 40, b: 40, l: 40, r: 40 }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot('errorRateChart', data, layout, config);
    }

    createHistogramBins(data, numBins) {
        const min = Math.min(...data);
        const max = Math.max(...data);
        const binSize = (max - min) / numBins;

        const bins = Array(numBins).fill(0);
        const labels = [];

        // Create bin labels
        for (let i = 0; i < numBins; i++) {
            const start = Math.round(min + i * binSize);
            const end = Math.round(min + (i + 1) * binSize);
            labels.push(`${start}-${end}`);
        }

        // Count data points in each bin
        data.forEach(value => {
            const binIndex = Math.min(Math.floor((value - min) / binSize), numBins - 1);
            bins[binIndex]++;
        });

        return { labels, data: bins };
    }

    updateCharts() {
        // Method to update all charts with new data
        if (this.charts.performance) {
            this.charts.performance.destroy();
            this.createPerformanceChart();
        }
        if (this.charts.responseTime) {
            this.charts.responseTime.destroy();
            this.createResponseTimeChart();
        }
        this.createErrorRateChart(); // Plotly charts update automatically
    }

    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Extend the PerformanceDashboard class to include chart functionality
if (typeof PerformanceDashboard !== 'undefined') {
    PerformanceDashboard.prototype.createPerformanceChart = function() {
        if (!this.chartManager) {
            this.chartManager = new ChartManager(this);
        }
        this.chartManager.createPerformanceChart();
    };

    PerformanceDashboard.prototype.createResponseTimeChart = function() {
        if (!this.chartManager) {
            this.chartManager = new ChartManager(this);
        }
        this.chartManager.createResponseTimeChart();
    };

    PerformanceDashboard.prototype.createErrorRateChart = function() {
        if (!this.chartManager) {
            this.chartManager = new ChartManager(this);
        }
        this.chartManager.createErrorRateChart();
    };
}
