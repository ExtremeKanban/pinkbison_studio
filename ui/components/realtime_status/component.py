"""
Simple HTML-based real-time status component with proper dark theme support.
"""

import streamlit as st
import streamlit.components.v1 as components


def realtime_status(project_name: str, key=None):
    """
    Render real-time status using simple HTML/JS component.
    Properly styled for Streamlit's dark theme.
    
    Args:
        project_name: Name of project to monitor
        key: Unique key for component instance
    """
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Source Sans Pro', sans-serif;
                background: transparent;
                color: #fafafa;
            }}
            .status-container {{
                background: transparent;
                padding: 0;
            }}
            .connection-status {{
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                font-size: 0.7rem;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
            }}
            .connected {{ 
                background: rgba(76, 175, 80, 0.2); 
                color: #81c784;
                border: 1px solid #4caf50;
            }}
            .disconnected {{ 
                background: rgba(244, 67, 54, 0.2); 
                color: #e57373;
                border: 1px solid #f44336;
            }}
            .status-section {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 0.75rem;
            }}
            .status-label {{
                font-weight: 600;
                color: #fafafa;
                font-size: 0.9rem;
            }}
            .status-badge {{
                padding: 0.3rem 0.75rem;
                border-radius: 4px;
                font-weight: 700;
                font-size: 0.8rem;
                letter-spacing: 0.5px;
            }}
            .status-idle {{ 
                background: rgba(158, 158, 158, 0.3); 
                color: #bdbdbd;
                border: 1px solid #9e9e9e;
            }}
            .status-running {{ 
                background: rgba(76, 175, 80, 0.3);
                color: #81c784;
                border: 1px solid #4caf50;
                animation: pulse 2s infinite;
            }}
            .status-paused {{ 
                background: rgba(255, 152, 0, 0.3);
                color: #ffb74d;
                border: 1px solid #ff9800;
            }}
            .status-completed {{ 
                background: rgba(33, 150, 243, 0.3);
                color: #64b5f6;
                border: 1px solid #2196f3;
            }}
            .status-error {{ 
                background: rgba(244, 67, 54, 0.3);
                color: #e57373;
                border: 1px solid #f44336;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
            .progress-container {{
                margin: 0.75rem 0;
                display: none;
            }}
            .progress-bar {{
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #2196f3, #64b5f6);
                width: 0%;
                transition: width 0.5s ease;
            }}
            .progress-text {{
                margin-top: 0.4rem;
                font-size: 0.8rem;
                color: #e0e0e0;
            }}
            .events-container {{
                margin-top: 0.75rem;
            }}
            .events-header {{
                font-weight: 600;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
                color: #fafafa;
            }}
            .events-stream {{
                max-height: 180px;
                overflow-y: auto;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 0.5rem;
                background: rgba(255, 255, 255, 0.03);
            }}
            .events-stream::-webkit-scrollbar {{
                width: 4px;
            }}
            .events-stream::-webkit-scrollbar-track {{
                background: transparent;
            }}
            .events-stream::-webkit-scrollbar-thumb {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }}
            .event-item {{
                padding: 0.4rem;
                margin-bottom: 0.3rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
                font-size: 0.8rem;
                border-left: 2px solid #2196f3;
                animation: slideIn 0.3s ease;
            }}
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(-10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            .event-time {{
                color: #9e9e9e;
                font-size: 0.7rem;
            }}
            .event-sender {{
                color: #64b5f6;
                font-weight: 600;
            }}
            .event-arrow {{
                color: #757575;
            }}
            .event-recipient {{
                color: #ba68c8;
                font-weight: 600;
            }}
            .event-type {{
                color: #bdbdbd;
                font-style: italic;
            }}
            .no-events {{
                text-align: center;
                color: #757575;
                padding: 1rem;
                font-size: 0.85rem;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="status-container">
            <div id="connection" class="connection-status disconnected">🔴 Connecting...</div>
            
            <div class="status-section">
                <span class="status-label">Pipeline Status:</span>
                <div id="status-badge" class="status-badge status-idle">IDLE</div>
            </div>
            
            <div id="progress-container" class="progress-container">
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill"></div>
                </div>
                <div id="progress-text" class="progress-text"></div>
            </div>
            
            <div class="events-container">
                <div class="events-header">📡 Live Events</div>
                <div id="events-stream" class="events-stream">
                    <div class="no-events">Waiting for events...</div>
                </div>
            </div>
        </div>

        <script>
            const projectName = '{project_name}';
            let ws = null;
            let reconnectAttempts = 0;

            function connect() {{
                console.log('[RealtimeStatus] Connecting...');
                ws = new WebSocket('ws://localhost:8765');

                ws.onopen = () => {{
                    console.log('[RealtimeStatus] Connected');
                    reconnectAttempts = 0;
                    document.getElementById('connection').className = 'connection-status connected';
                    document.getElementById('connection').textContent = '🟢 Connected';
                    
                    ws.send(JSON.stringify({{
                        action: 'subscribe',
                        project: projectName
                    }}));
                }};

                ws.onmessage = (event) => {{
                    try {{
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'pipeline_status') {{
                            updateStatus(data.data);
                        }} else if (data.type === 'pipeline_progress') {{
                            updateProgress(data.data);
                        }} else if (data.type === 'eventbus_message') {{
                            addEvent(data.data);
                        }}
                    }} catch (error) {{
                        console.error('[RealtimeStatus] Error:', error);
                    }}
                }};

                ws.onerror = () => {{
                    document.getElementById('connection').className = 'connection-status disconnected';
                    document.getElementById('connection').textContent = '🔴 Disconnected';
                }};

                ws.onclose = () => {{
                    document.getElementById('connection').className = 'connection-status disconnected';
                    document.getElementById('connection').textContent = '🔴 Disconnected';
                    
                    if (reconnectAttempts < 5) {{
                        reconnectAttempts++;
                        setTimeout(connect, Math.min(1000 * Math.pow(2, reconnectAttempts), 30000));
                    }}
                }};
            }}

            function updateStatus(status) {{
                const badge = document.getElementById('status-badge');
                badge.textContent = status.status.toUpperCase();
                badge.className = 'status-badge status-' + status.status;
                
                const progressContainer = document.getElementById('progress-container');
                progressContainer.style.display = (status.status === 'running') ? 'block' : 'none';
            }}

            function updateProgress(progress) {{
                const fill = document.getElementById('progress-fill');
                fill.style.width = Math.round(progress.percent_complete) + '%';
                
                const text = document.getElementById('progress-text');
                text.textContent = progress.current_step + ' - Step ' + 
                    progress.step_number + '/' + progress.total_steps + 
                    ' (' + Math.round(progress.percent_complete) + '%)';
            }}

            function addEvent(event) {{
                const stream = document.getElementById('events-stream');
                
                // Remove "waiting" message if present
                const noEvents = stream.querySelector('.no-events');
                if (noEvents) {{
                    stream.removeChild(noEvents);
                }}
                
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event-item';
                const time = new Date().toLocaleTimeString();
                eventDiv.innerHTML = 
                    '<span class="event-time">' + time + '</span> ' +
                    '<span class="event-sender">' + event.sender + '</span> ' +
                    '<span class="event-arrow">→</span> ' +
                    '<span class="event-recipient">' + event.recipient + '</span> ' +
                    '<span class="event-type">' + event.event_type + '</span>';
                
                stream.insertBefore(eventDiv, stream.firstChild);
                
                // Keep only last 50 events
                while (stream.children.length > 50) {{
                    stream.removeChild(stream.lastChild);
                }}
            }}

            // Connect on load
            connect();
        </script>
    </body>
    </html>
    """
    
    # Render as HTML component - scrolling=False removes gap
    components.html(html_code, height=350, scrolling=False)