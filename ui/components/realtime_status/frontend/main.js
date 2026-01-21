// Real-Time Status Component with WebSocket
class RealtimeStatus {
    constructor() {
        this.ws = null;
        this.projectName = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    // Connect to WebSocket server
    connect(projectName) {
        this.projectName = projectName;
        
        console.log('[RealtimeStatus] Connecting to ws://localhost:8765');
        this.ws = new WebSocket('ws://localhost:8765');

        this.ws.onopen = () => {
            console.log('[RealtimeStatus] Connected successfully');
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            
            // Subscribe to project events
            this.ws.send(JSON.stringify({
                action: 'subscribe',
                project: this.projectName
            }));
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('[RealtimeStatus] Parse error:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('[RealtimeStatus] WebSocket error:', error);
            this.updateConnectionStatus(false);
        };

        this.ws.onclose = () => {
            console.log('[RealtimeStatus] Connection closed');
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        };
    }

    // Handle incoming WebSocket messages
    handleMessage(data) {
        switch(data.type) {
            case 'pipeline_status':
                this.updatePipelineStatus(data.data);
                break;
            case 'pipeline_progress':
                this.updateProgress(data.data);
                break;
            case 'eventbus_message':
                this.addEvent(data.data);
                break;
            default:
                console.log('[RealtimeStatus] Unknown message:', data.type);
        }
    }

    // Update pipeline status badge
    updatePipelineStatus(status) {
        const badge = document.getElementById('status-badge');
        if (badge) {
            badge.textContent = status.status.toUpperCase();
            badge.className = `status-badge status-${status.status}`;
        }

        const task = document.getElementById('current-task');
        if (task && status.current_task) {
            task.textContent = status.current_task;
            task.style.display = 'block';
        } else if (task) {
            task.style.display = 'none';
        }

        // Show/hide progress section
        const progressSection = document.getElementById('progress-section');
        if (progressSection) {
            progressSection.style.display = 
                (status.status === 'running') ? 'block' : 'none';
        }
    }

    // Update progress bar
    updateProgress(progress) {
        const bar = document.getElementById('progress-bar');
        if (bar) {
            bar.style.width = Math.round(progress.percent_complete) + '%';
        }

        const text = document.getElementById('progress-text');
        if (text) {
            text.textContent = 
                `${progress.current_step} - ` +
                `Step ${progress.step_number}/${progress.total_steps} ` +
                `(${Math.round(progress.percent_complete)}%)`;
        }
    }

    // Add event to live stream
    addEvent(event) {
        const stream = document.getElementById('event-stream');
        if (!stream) return;

        const eventDiv = document.createElement('div');
        eventDiv.className = 'event-item';
        
        const time = new Date().toLocaleTimeString();
        eventDiv.innerHTML = `
            <span class="event-time">${time}</span>
            <span class="event-sender">${event.sender}</span>
            <span class="event-arrow">→</span>
            <span class="event-recipient">${event.recipient}</span>
            <span class="event-type">${event.event_type}</span>
        `;

        // Insert at top
        stream.insertBefore(eventDiv, stream.firstChild);

        // Keep only last 50 events
        while (stream.children.length > 50) {
            stream.removeChild(stream.lastChild);
        }
    }

    // Update connection indicator
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            if (connected) {
                indicator.textContent = '🟢 Connected';
                indicator.className = 'connection-status connected';
            } else {
                indicator.textContent = '🔴 Disconnected';
                indicator.className = 'connection-status disconnected';
            }
        }
    }

    // Attempt to reconnect with exponential backoff
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[RealtimeStatus] Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
            30000  // Max 30 seconds
        );

        console.log(`[RealtimeStatus] Reconnecting in ${delay}ms...`);
        setTimeout(() => this.connect(this.projectName), delay);
    }

    // Disconnect and cleanup
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Initialize global instance
window.realtimeStatus = new RealtimeStatus();

// Streamlit component callbacks
function onRender(event) {
    const data = event.detail;
    
    // Connect if not already connected
    if (data.project_name && !window.realtimeStatus.ws) {
        window.realtimeStatus.connect(data.project_name);
    }
}

function onUnmount() {
    if (window.realtimeStatus) {
        window.realtimeStatus.disconnect();
    }
}