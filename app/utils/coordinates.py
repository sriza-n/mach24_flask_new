"""
Coordinate transformation utilities.
"""

# Import pyproj after eventlet monkey patching
from pyproj import Transformer, CRS


def xy_to_latlon(x_meters, y_meters, alt_meters, origin_lat, origin_lon):
    """
    Convert local X,Y coordinates (in meters) to lat/lon
    using a local tangent plane projection (transverse mercator)
    
    Parameters:
    -----------
    x_meters : float
        X coordinate in meters from origin
    y_meters : float
        Y coordinate in meters from origin
    alt_meters : float
        Altitude in meters above ground level
    origin_lat : float
        Latitude of the origin point
    origin_lon : float
        Longitude of the origin point
        
    Returns:
    --------
    tuple: (latitude, longitude, altitude)
        Converted WGS84 coordinates
    """
    # Create a transformer from local XY meters to WGS84 lat/lon
    transformer = Transformer.from_crs(
        # Local tangent plane centered at origin
        CRS.from_proj4(f"+proj=tmerc +lat_0={origin_lat} +lon_0={origin_lon} +k=1 +x_0=0 +y_0=0"),
        CRS.from_epsg(4326),  # Used by Google Maps, OpenStreetMap, and other web mapping services
        always_xy=True
    )
    
    # Transform the coordinates including altitude
    lon, lat, alt = transformer.transform(x_meters, y_meters, alt_meters)
    return lat, lon, alt
