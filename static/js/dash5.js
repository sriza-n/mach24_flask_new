// Your access token can be found at: https://ion.cesium.com/tokens.
// This is the default access token from your ion account
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjZTRiMDNmNy03NzkyLTQ0NDEtOTU0Zi1hNWUyNGI3ZjIwYzciLCJpZCI6MzAxNjkzLCJpYXQiOjE3NDcwNDEwNjJ9.yDea13y1sQQ_QDA77GUYwghK3SQ85HM1YLxHc4tvntE';

// Initialize the Cesium viewer
const viewer = new Cesium.Viewer('cesiumContainer', {
    terrain: Cesium.Terrain.fromWorldTerrain(),
    infoBox: false,
    selectionIndicator: false,
    shadows: true,
    shouldAnimate: true,
});

const osmBuildings = await Cesium.createOsmBuildingsAsync();
viewer.scene.primitives.add(osmBuildings);

const initialData = window.flaskData;
// console.log('Data received from Flask:', initialData);
// console.log('Number of records received:', initialData.length);
const timeSet = new Set();
// Prepare data arrays - similar to visualize.js approach
var timeData = [];
var xPosData = [];
var yPosData = [];
var altData = [];
var euler = [];

// Process initial data
initialData.forEach(record => {
    const Time = parseFloat(record.teensytime);
    const lat = parseFloat(record.fused_lat);
    const lon = parseFloat(record.fused_lon);
    const alt = parseFloat(record.alt);
    const eu_x = parseFloat(record.eu_x);
    const eu_y = parseFloat(record.eu_y);
    const eu_z = parseFloat(record.eu_z);

    // Update data arrays
    timeData.unshift(Time);
    xPosData.unshift(lat);
    yPosData.unshift(lon);
    altData.unshift(alt);
    euler.unshift([eu_x, eu_y, eu_z]);
    timeSet.add(Time);
});

// Create a proper flightData object with the arrays we've built
const flightData = {
    timeData: timeData,
    xPosData: xPosData,
    yPosData: yPosData,
    altData: altData
};

// Now this will work
// console.log('Flight data:', flightData.timeData);

// Initialize the viewer clock
const timeStepInSeconds = 1; // Assuming radar samples are 1 seconds apart
const totalDataPoints = flightData.timeData.length;
const totalSeconds = timeStepInSeconds * (totalDataPoints - 1);

// Start time in UTC
const start = Cesium.JulianDate.fromIso8601("2025-03-09T23:10:00Z");
const stop = Cesium.JulianDate.addSeconds(start, totalSeconds, new Cesium.JulianDate());

// Configure the clock and timeline
viewer.clock.startTime = start.clone();
viewer.clock.stopTime = stop.clone();
viewer.clock.currentTime = start.clone();
viewer.timeline.zoomTo(start, stop);

// Speed up the playback
viewer.clock.multiplier = 1;
viewer.clock.shouldAnimate = true;

// The SampledPositionProperty stores the position and timestamp for each sample
const positionProperty = new Cesium.SampledPositionProperty();

// Add position samples based on our data arrays
for (let i = 0; i < totalDataPoints; i++) {
    // Calculate time for this sample
    const time = Cesium.JulianDate.addSeconds(start, i * timeStepInSeconds, new Cesium.JulianDate());

    // Get coordinates from our data arrays (note: xPosData is latitude, yPosData is longitude)
    const latitude = flightData.xPosData[i];
    const longitude = flightData.yPosData[i];
    const altitude = flightData.altData[i];

    // Create position from coordinates
    const position = Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude);

    // Add sample to position property
    positionProperty.addSample(time, position);

    // Add point entity at each position
    viewer.entities.add({
        description: `Location: (${longitude}, ${latitude}, ${altitude})`,
        position: Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude),
        point: {
            pixelSize: 5,
            color: Cesium.Color.RED
        }
    });
}

// Create the airplane entity that will move along the path
const rocketEntity = viewer.entities.add({
    availability: new Cesium.TimeIntervalCollection([
        new Cesium.TimeInterval({ start: start, stop: stop })
    ]),
    position: positionProperty,
    point: {
        pixelSize: 30,
        color: Cesium.Color.GREEN
    },
    path: new Cesium.PathGraphics({
        width: 3,
        material: Cesium.Color.WHITE,
        leadTime: 0,
        trailTime: Infinity,
        resolution: 1
    }),
    // Add orientation based on Euler angles
    orientation: new Cesium.VelocityOrientationProperty(positionProperty)
});

// Create a property to store orientation data for each time point
const orientationProperty = new Cesium.SampledProperty(Cesium.Quaternion);

// Helper function to convert Euler angles to quaternion
function eulerToQuaternion(position, eulerX, eulerY, eulerZ) {
    // Convert from degrees to radians
    const radX = Cesium.Math.toRadians(eulerX);
    const radY = Cesium.Math.toRadians(eulerY);
    const radZ = Cesium.Math.toRadians(360 - eulerZ);

    // Map Euler angles to Cesium's heading/pitch/roll
    // Note: This mapping depends on your sensor's coordinate system
    const heading = radX;
    const pitch = radY;
    const roll = radZ;

    // Create the orientation quaternion
    const hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
    return Cesium.Transforms.headingPitchRollQuaternion(position, hpr);
}

// Process Euler angles for each data point
for (let i = 0; i < totalDataPoints; i++) {
    const time = Cesium.JulianDate.addSeconds(start, i * timeStepInSeconds, new Cesium.JulianDate());

    // Get coordinates and Euler angles
    const latitude = flightData.xPosData[i];
    const longitude = flightData.yPosData[i];
    const altitude = flightData.altData[i];
    const eulerAngles = euler[i];

    // Get position as Cartesian3
    const position = Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude);

    // Create quaternion from Euler angles and position
    const quaternion = eulerToQuaternion(position, eulerAngles[0], eulerAngles[1], eulerAngles[2]);

    // Add orientation sample
    orientationProperty.addSample(time, quaternion);
}

// Set the rocket's orientation
rocketEntity.orientation = orientationProperty;

// Instead of using polylines for orientation axes, use a model
// that automatically shows orientation
const rocketModelEntity = viewer.entities.add({
    position: positionProperty,
    orientation: orientationProperty,
    model: {
        uri: '/static/assets/rocket.glb',
        minimumPixelSize: 64,
        maximumScale: 20000,
        scale: 0.009,
    }
});

// Make the camera track this moving entity
viewer.trackedEntity = rocketEntity;

// Function to get terrain height at a specific lat/lon
async function getTerrainHeight(longitude, latitude) {
    // Create a Cartographic position (longitude, latitude in radians, height 0)
    const position = Cesium.Cartographic.fromDegrees(longitude, latitude);

    try {
        // Check if terrain provider exists and is ready
        if (!viewer.terrainProvider) {
            console.warn('Terrain provider not available');
            return 0;
        }

        // Use a different approach that doesn't rely on readyPromise
        // Sample the terrain height at the highest available level of detail
        const updatedPositions = await Cesium.sampleTerrain(
            viewer.terrainProvider,
            15, // Level of detail (0-15, where 15 is highest)
            [position]
        );

        // Return the height in meters
        return updatedPositions[0].height;
    } catch (error) {
        console.error('Error sampling terrain:', error);
        return 0; // Default height
    }
}

// Wait for the globe to be fully loaded before querying terrain
function checkTerrainLoaded() {
    if (!viewer.scene.globe.tilesLoaded) {
        // Not ready yet, try again in a moment
        setTimeout(checkTerrainLoaded, 100);
        return;
    }

    // Globe is ready, now we can query terrain heights
    const lon = flightData.yPosData[0]; // First data point longitude
    const lat = flightData.xPosData[0]; // First data point latitude

    getTerrainHeight(lon, lat).then(height => {
        console.log(`Ground elevation at (${lon}, ${lat}): ${height} meters`);
    });
}

// Start checking if terrain is loaded
checkTerrainLoaded();
