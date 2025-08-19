"""
Database models for the Mach24 application.
"""

from flask_sqlalchemy import SQLAlchemy
from app import db


class SensorData(db.Model):
    """Model for sensor data when ST=1."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.Integer, nullable=False)
    x_pos = db.Column(db.Float, nullable=False)
    y_pos = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    eu_x = db.Column(db.Float, nullable=False)
    eu_y = db.Column(db.Float, nullable=False)
    eu_z = db.Column(db.Float, nullable=False)
    acc = db.Column(db.Float, nullable=False)  # Changed from acc_x, acc_y, acc_z to single acc
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)
    snr = db.Column(db.Float, nullable=False, default=0.0)
    # New fields from your serial data
    p1 = db.Column(db.Float, nullable=False, default=0.0)
    p2 = db.Column(db.Float, nullable=False, default=0.0)
    load = db.Column(db.Float, nullable=False, default=0.0)
    servo1_angle = db.Column(db.Integer, nullable=False, default=0)
    servo2_angle = db.Column(db.Integer, nullable=False, default=0)
    config_mode = db.Column(db.Integer, nullable=False, default=0)
    test_mode = db.Column(db.Integer, nullable=False, default=0)
    connection_state = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "teensytime": self.teensytime,
            "record_sn": self.record_sn,
            "voltage": self.voltage,
            "current": self.current,
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "alt": self.alt,
            "eu_x": self.eu_x,
            "eu_y": self.eu_y,
            "eu_z": self.eu_z,
            "acc": self.acc,
            "lat": self.lat,
            "lon": self.lon,
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr,
            "p1": self.p1,
            "p2": self.p2,
            "load": self.load,
            "servo1_angle": self.servo1_angle,
            "servo2_angle": self.servo2_angle,
            "config_mode": self.config_mode,
            "test_mode": self.test_mode,
            "connection_state": self.connection_state
        }


class SensorData0(db.Model):
    """Model for sensor data when ST=0."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.Integer, nullable=False)
    x_pos = db.Column(db.Float, nullable=False)
    y_pos = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    eu_x = db.Column(db.Float, nullable=False)
    eu_y = db.Column(db.Float, nullable=False)
    eu_z = db.Column(db.Float, nullable=False)
    acc = db.Column(db.Float, nullable=False)  # Changed from acc_x, acc_y, acc_z to single acc
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)
    snr = db.Column(db.Float, nullable=False, default=0.0)
    # New fields from your serial data
    p1 = db.Column(db.Float, nullable=False, default=0.0)
    p2 = db.Column(db.Float, nullable=False, default=0.0)
    load = db.Column(db.Float, nullable=False, default=0.0)
    servo1_angle = db.Column(db.Integer, nullable=False, default=0)
    servo2_angle = db.Column(db.Integer, nullable=False, default=0)
    config_mode = db.Column(db.Integer, nullable=False, default=0)
    test_mode = db.Column(db.Integer, nullable=False, default=0)
    connection_state = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "teensytime": self.teensytime,
            "record_sn": self.record_sn,
            "voltage": self.voltage,
            "current": self.current,
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "alt": self.alt,
            "eu_x": self.eu_x,
            "eu_y": self.eu_y,
            "eu_z": self.eu_z,
            "acc": self.acc,
            "lat": self.lat,
            "lon": self.lon,
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr,
            "p1": self.p1,
            "p2": self.p2,
            "load": self.load,
            "servo1_angle": self.servo1_angle,
            "servo2_angle": self.servo2_angle,
            "config_mode": self.config_mode,
            "test_mode": self.test_mode,
            "connection_state": self.connection_state
        }


class SwitchState(db.Model):
    """Model for storing switch and valve state data."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    record_sn = db.Column(db.String(20), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    remote_st = db.Column(db.Integer, nullable=False)
    valve_1 = db.Column(db.Integer, nullable=False)
    valve_2 = db.Column(db.Integer, nullable=False)
    activ_st = db.Column(db.Integer, nullable=False)
    igni_st = db.Column(db.Integer, nullable=False)
    para_st = db.Column(db.Integer, nullable=False)
    x_pos = db.Column(db.Float, nullable=False)
    y_pos = db.Column(db.Float, nullable=False)
    alt = db.Column(db.Float, nullable=False)
    eu_x = db.Column(db.Float, nullable=False)
    eu_y = db.Column(db.Float, nullable=False)
    eu_z = db.Column(db.Float, nullable=False)
    acc = db.Column(db.Float, nullable=False)  # Changed from acc_x, acc_y, acc_z to single acc
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    fused_lat = db.Column(db.Float, nullable=False)
    fused_lon = db.Column(db.Float, nullable=False)
    rssi = db.Column(db.Float, nullable=False, default=0.0)
    snr = db.Column(db.Float, nullable=False, default=0.0)
    # New fields from your serial data
    p1 = db.Column(db.Float, nullable=False, default=0.0)
    p2 = db.Column(db.Float, nullable=False, default=0.0)
    load = db.Column(db.Float, nullable=False, default=0.0)
    servo1_angle = db.Column(db.Integer, nullable=False, default=0)
    servo2_angle = db.Column(db.Integer, nullable=False, default=0)
    config_mode = db.Column(db.Integer, nullable=False, default=0)
    test_mode = db.Column(db.Integer, nullable=False, default=0)
    connection_state = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "time": self.time,
            "teensytime": self.teensytime,
            "record_sn": self.record_sn,
            "voltage": self.voltage,
            "current": self.current,
            "remote_st": self.remote_st,
            "valve_1": self.valve_1,
            "valve_2": self.valve_2,
            "activ_st": self.activ_st,
            "igni_st": self.igni_st,
            "para_st": self.para_st,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "alt": self.alt,
            "eu_x": self.eu_x,
            "eu_y": self.eu_y,
            "eu_z": self.eu_z,
            "acc": self.acc,
            "lat": self.lat,
            "lon": self.lon,
            "fused_lat": self.fused_lat,
            "fused_lon": self.fused_lon,
            "rssi": self.rssi,
            "snr": self.snr,
            "p1": self.p1,
            "p2": self.p2,
            "load": self.load,
            "servo1_angle": self.servo1_angle,
            "servo2_angle": self.servo2_angle,
            "config_mode": self.config_mode,
            "test_mode": self.test_mode,
            "connection_state": self.connection_state
        }
