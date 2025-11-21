// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.refreshInterval = 2000; // 2 seconds
        this.intervalId = null;
        this.config = {};
        this.init();
    }

    async init() {
        // Load configuration
        await this.loadConfig();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Load initial data
        await this.updateDashboard();
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            this.config = await response.json();
            
            // Update title if configured
            if (this.config.title) {
                document.getElementById('dashboard-title').textContent = this.config.title;
            }
            
            // Update refresh interval if configured
            if (this.config.refresh_interval) {
                this.refreshInterval = this.config.refresh_interval;
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }
    }

    startAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        
        this.intervalId = setInterval(() => {
            this.updateDashboard();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async updateDashboard() {
        try {
            const response = await fetch('/api/progress');
            const progress = await response.json();
            
            if (progress.status === 'not_started' || progress.status === 'error') {
                this.displayError(progress.message || 'No data available');
                return;
            }
            
            this.updateUI(progress);
        } catch (error) {
            console.error('Error updating dashboard:', error);
            this.displayError('Error connecting to server');
        }
    }

    updateUI(progress) {
        // Update status
        this.updateStatus(progress.status);
        
        // Update overall progress
        this.updateOverallProgress(progress);
        
        // Update time estimates
        this.updateTimeEstimates(progress.estimated_time || {});
        
        // Update listings statistics
        this.updateListingsStats(progress.listings || {});
        
        // Update errors
        this.updateErrors(progress.errors || 0);
        
        // Update workers
        this.updateWorkers(progress.workers || {});
        
        // Update last update time
        this.updateLastUpdate(progress.last_update);
    }

    updateStatus(status) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        statusDot.className = 'status-dot ' + status;
        
        const statusLabels = {
            'running': 'Running',
            'completed': 'Completed',
            'error': 'Error',
            'paused': 'Paused',
            'initializing': 'Initializing',
        };
        
        statusText.textContent = statusLabels[status] || status;
    }

    updateOverallProgress(progress) {
        const work = progress.total_work || {};
        const unit = work.unit || 'pages';
        
        // Progress bar
        const percentage = work.percentage || 0;
        document.getElementById('progress-fill').style.width = percentage + '%';
        document.getElementById('progress-percentage').textContent = percentage.toFixed(1) + '%';
        document.getElementById('progress-details').textContent = 
            `${work.completed || 0} / ${work.total || 0} ${unit}`;
        
        // Stats
        document.getElementById('stat-completed').textContent = work.completed || 0;
        document.getElementById('stat-remaining').textContent = work.remaining || 0;
        document.getElementById('stat-total').textContent = work.total || 0;
    }

    updateTimeEstimates(timeData) {
        // Elapsed time
        const elapsed = this.formatTime(timeData.elapsed_seconds || 0);
        document.getElementById('time-elapsed').textContent = elapsed;

        // Remaining time
        const remaining = timeData.remaining_seconds || 0;
        if (remaining > 0) {
            document.getElementById('time-remaining').textContent = this.formatTime(remaining);
        } else {
            document.getElementById('time-remaining').textContent = '-';
        }

        // Rate
        const rate = timeData.rate_per_minute || 0;
        document.getElementById('time-rate').textContent = rate.toFixed(1) + '/min';

        // Estimated completion - show only time, not full date
        if (timeData.estimated_completion) {
            const completion = new Date(timeData.estimated_completion);
            document.getElementById('time-completion').textContent =
                completion.toLocaleTimeString();
        } else {
            document.getElementById('time-completion').textContent = '-';
        }
    }

    updateListingsStats(listings) {
        document.getElementById('listings-found').textContent = listings.found || 0;
        document.getElementById('listings-extracted').textContent = listings.extracted || 0;
        document.getElementById('listings-saved').textContent = listings.saved || 0;
        document.getElementById('listings-duplicates').textContent = listings.duplicates_skipped || 0;
        document.getElementById('listings-failed').textContent = listings.failed || 0;
    }

    updateErrors(errors) {
        document.getElementById('stat-errors').textContent = errors || 0;
    }

    updateWorkers(workers) {
        const section = document.getElementById('workers-section');
        const container = document.getElementById('workers-container');

        // Hide workers section if no workers
        if (!workers || Object.keys(workers).length === 0) {
            section.style.display = 'none';
            return;
        }

        // Show workers section
        section.style.display = 'block';
        container.innerHTML = '';

        // Sort workers by ID
        const workerIds = Object.keys(workers).sort((a, b) => parseInt(a) - parseInt(b));

        workerIds.forEach(workerId => {
            const worker = workers[workerId];
            const workerItem = this.createWorkerElement(workerId, worker);
            container.appendChild(workerItem);
        });
    }

    createWorkerElement(workerId, worker) {
        const div = document.createElement('div');
        div.className = 'worker-item ' + (worker.status || 'running');
        
        const statusClass = (worker.status || 'running').toLowerCase();
        
        div.innerHTML = `
            <div class="worker-header">
                <span class="worker-name">Worker ${workerId}</span>
                <span class="worker-status ${statusClass}">${worker.status || 'Running'}</span>
            </div>
            <div class="worker-stats">
                <div class="worker-stat">
                    <div class="worker-stat-label">Pages</div>
                    <div class="worker-stat-value">${worker.pages_processed || 0}</div>
                </div>
                <div class="worker-stat">
                    <div class="worker-stat-label">URLs Found</div>
                    <div class="worker-stat-value">${worker.urls_found || 0}</div>
                </div>
                <div class="worker-stat">
                    <div class="worker-stat-label">Extracted</div>
                    <div class="worker-stat-value">${worker.listings_extracted || 0}</div>
                </div>
                <div class="worker-stat">
                    <div class="worker-stat-label">Errors</div>
                    <div class="worker-stat-value error">${worker.errors || 0}</div>
                </div>
            </div>
        `;
        
        return div;
    }

    updateLastUpdate(timestamp) {
        if (!timestamp) return;

        const date = new Date(timestamp);
        document.getElementById('last-update').textContent = date.toLocaleTimeString();
    }

    displayError(message) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        statusDot.className = 'status-dot error';
        statusText.textContent = message;
    }

    formatTime(seconds) {
        if (seconds < 60) {
            return Math.floor(seconds) + 's';
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${minutes}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours}h ${minutes}m ${secs}s`;
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

