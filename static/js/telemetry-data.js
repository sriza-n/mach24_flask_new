class TelemetryDataManager {
    constructor() {
        this.currentData = {};
        this.subscribers = [];
        this.isConnected = false;
        this.fetchInterval = null;
    }

    // Subscribe to data updates
    subscribe(callback) {
        this.subscribers.push(callback);
        // Immediately call with current data if available
        if (Object.keys(this.currentData).length > 0) {
            callback(this.currentData);
        }
    }

    // Unsubscribe from data updates
    unsubscribe(callback) {
        this.subscribers = this.subscribers.filter(sub => sub !== callback);
    }

    // Notify all subscribers of data update
    notifySubscribers(data) {
        this.subscribers.forEach(callback => callback(data));
    }

    // Start fetching data
    startFetching(interval = 1000) {
        if (this.fetchInterval) {
            clearInterval(this.fetchInterval);
        }
        
        this.fetchData(); // Initial fetch
        this.fetchInterval = setInterval(() => this.fetchData(), interval);
    }

    // Stop fetching data
    stopFetching() {
        if (this.fetchInterval) {
            clearInterval(this.fetchInterval);
            this.fetchInterval = null;
        }
    }

    // Fetch data from server
    async fetchData() {
        try {
            const response = await fetch('/latest_sw');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const newData = await response.json();
            console.log('Latest data fetched:', newData);
            
            // Parse and store the data
            this.currentData = this.parseData(newData);
            this.isConnected = true;
            
            // Update connection status
            this.updateConnectionStatus(true);
            
            // Notify all subscribers
            this.notifySubscribers(this.currentData);
            
        } catch (error) {
            console.error('Error fetching data:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }

    // Parse raw data into structured format
    parseData(record) {
        return {
            // Time data
            teensyTime: record.teensytime || '--',
            time: record.time,
            date: record.date,
            
            // System data
            recordSn: record.record_sn,
            current: parseFloat(record.current) || 0,
            voltage: parseFloat(record.voltage) || 0,
            
            // Ground remote state connected or not
            remoteSt: parseFloat(record.connection_state) || 0,
            // Activation state before ignition
            activSt: parseFloat(record.activ_st) || 0,
            // Ignition state
            igniSt: parseFloat(record.igni_st) || 0,
            // Parachute deployment state
            paraSt: parseFloat(record.para_st) || 0,
            //creates hotspot on rocket for configuration with hotspot name "RocketConfig🚀" if high
            configMode: parseFloat(record.config_mode) || 0,
            // Test mode between ground test or flight test
            testMode: parseFloat(record.test_mode) || 0,
            
            // Servo data
            servo1state: parseFloat(record.valve_1) || 0,
            servo2state: parseFloat(record.valve_2) || 0,
            servo1Angle: parseFloat(record.servo1_angle) || 0,
            servo2Angle: parseFloat(record.servo2_angle) || 0,
            
            // on flight test test mode is 0, gets flight data lat, lon, acc, eu_x, eu_y, eu_z, fused_lat, fused_lon, x_pos, y_pos, alt
            lat: parseFloat(record.lat) || 0,
            lon: parseFloat(record.lon) || 0,
            acc: parseFloat(record.acc) || 0,
            euX: parseFloat(record.eu_x) || 0,
            euY: parseFloat(record.eu_y) || 0,
            euZ: parseFloat(record.eu_z) || 0,
            fusedLat: parseFloat(record.fused_lat) || 0,
            fusedLon: parseFloat(record.fused_lon) || 0,
            xPos: parseFloat(record.x_pos) || 0,
            yPos: parseFloat(record.y_pos) || 0,
            altitude: parseFloat(record.alt) || 0,
            
            // Ground test data (available when testMode === 1)
            p1: parseFloat(record.p1) || 0,
            p2: parseFloat(record.p2) || 0,
            load: parseFloat(record.load) || 0,
            
            // Signal quality
            rssi: parseFloat(record.rssi) || 0,
            snr: parseFloat(record.snr) || 0
        };
    }

    // Update connection status indicator with enhanced feedback
    updateConnectionStatus(connected) {
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            connectionStatus.className = connected 
                ? 'w-2 h-2 rounded-full bg-green-500 status-indicator animate-pulse'
                : 'w-2 h-2 rounded-full bg-red-500 status-indicator';
        }

        const lastUpdate = document.getElementById('last-update');
        if (lastUpdate && connected) {
            const now = new Date();
            lastUpdate.textContent = now.toLocaleTimeString();
        }
    }

    // Get current data
    getCurrentData() {
        return this.currentData;
    }

    // Get specific data value
    getValue(key) {
        return this.currentData[key];
    }

    // Check if connected
    getConnectionStatus() {
        return this.isConnected;
    }
}

// Create global instance
window.telemetryManager = new TelemetryDataManager();