// reconmaster/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    const toolList = document.getElementById('tool-list');
    const mainContent = document.getElementById('main-content');

    // --- WebSocket variable, kept null until a connection is made ---
    let socket = null;

    // --- Function to fetch all tools (no changes) ---
    async function fetchTools() {
        try {
            const response = await fetch('/api/tools');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const tools = await response.json();
            displayTools(tools);
        } catch (error) {
            console.error("Failed to fetch tools:", error);
            toolList.innerHTML = '<p class="p-3 text-danger">Failed to load tools.</p>';
        }
    }

    // --- Function to display all tools (no changes) ---
    function displayTools(tools) {
        toolList.innerHTML = '';
        if (tools.length === 0) {
            toolList.innerHTML = '<p class="p-3 text-muted">No tools found.</p>';
            return;
        }
        tools.forEach(tool => {
            const toolElement = document.createElement('a');
            toolElement.href = '#';
            toolElement.className = 'list-group-item list-group-item-action';
            toolElement.textContent = tool.name;
            toolElement.dataset.toolId = tool.id;
            toolList.appendChild(toolElement);
        });
    }

    // --- Function to fetch and display details for a single tool (no changes) ---
    async function fetchAndDisplayToolDetails(toolId) {
        try {
            const response = await fetch(`/api/tools/${toolId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const tool = await response.json();
            updateMainContent(tool);
        } catch (error) {
            console.error("Failed to fetch tool details:", error);
            mainContent.innerHTML = '<p class="text-danger">Error loading tool details.</p>';
        }
    }

    // --- Function to update the main content area with tool info (no changes) ---
    function updateMainContent(tool) {
        mainContent.innerHTML = `
            <h2 class="card-title">${tool.name} <span class="badge bg-secondary">${tool.category}</span></h2>
            <p class="card-text">${tool.description}</p>
            
            <h5>Advantages</h5>
            <p>${tool.advantages}</p>

            <h5>Example Usage</h5>
            <pre><code>${tool.example_usage}</code></pre>
            
            <hr>

            <h4>Run Tool</h4>
            <div class="mb-3">
                <label for="target-input" class="form-label">Target (e.g., IP Address or Domain)</label>
                <input type="text" class="form-control" id="target-input" placeholder="example.com">
            </div>
            <button class="btn btn-primary" id="run-tool-btn" data-tool-id="${tool.id}">Run Scan</button>
            
            <h4 class="mt-4">Output</h4>
            <div id="output-area" class="mt-2">
                <!-- Command output will appear here -->
            </div>
        `;
    }

    // --- Event Delegation for the entire main content area ---
    mainContent.addEventListener('click', function(event) {
        // Check if the "Run Scan" button was clicked
        if (event.target && event.target.id === 'run-tool-btn') {
            const toolId = event.target.dataset.toolId;
            const targetInput = document.getElementById('target-input');
            const target = targetInput.value.trim();
            const outputArea = document.getElementById('output-area');

            if (!target) {
                outputArea.textContent = 'ERROR: Please enter a target.';
                return;
            }

            // Close any existing WebSocket connection before starting a new one
            if (socket) {
                socket.close();
            }

            // Start the WebSocket connection
            startWebSocket(toolId, target, outputArea);
        }
    });
    
    // --- NEW: Function to handle the WebSocket connection ---
    function startWebSocket(toolId, target, outputArea) {
        // Clear previous output
        outputArea.innerHTML = '<p class="text-info">Connecting to server...</p>';

        // Determine the correct protocol (ws or wss)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/run/${toolId}`;
        
        socket = new WebSocket(wsUrl);

        socket.onopen = function(event) {
            console.log("WebSocket connection established.");
            outputArea.innerHTML = '<p class="text-success">Connection successful! Sending target...</p>';
            // Send the target to the server
            socket.send(target);
        };

        socket.onmessage = function(event) {
            // When a message is received, append it to the output area
            const message = document.createElement('div');
            message.textContent = event.data;
            outputArea.appendChild(message);
            // Auto-scroll to the bottom
            outputArea.scrollTop = outputArea.scrollHeight;
        };

        socket.onclose = function(event) {
            console.log("WebSocket connection closed.", event);
            const message = document.createElement('p');
            message.className = 'text-warning mt-2';
            message.textContent = 'Connection closed.';
            outputArea.appendChild(message);
        };

        socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            const message = document.createElement('p');
            message.className = 'text-danger mt-2';
            message.textContent = 'An error occurred with the connection.';
            outputArea.appendChild(message);
        };
    }

    // --- Click listener for the tool list (no changes) ---
    toolList.addEventListener('click', function(event) {
        if (event.target && event.target.matches('a.list-group-item-action')) {
            event.preventDefault();
            const toolId = event.target.dataset.toolId;
            if (toolId) {
                fetchAndDisplayToolDetails(toolId);
            }
        }
    });

    // Initial fetch of tools when the page loads
    fetchTools();
});
