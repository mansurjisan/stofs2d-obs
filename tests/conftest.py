"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def mock_fort61_file(temp_dir):
    """Create a mock fort.61.nc file for testing"""
    import netCDF4 as nc

    filepath = Path(temp_dir) / 'test_fort.61.nc'

    # Create NetCDF file
    ds = nc.Dataset(filepath, 'w', format='NETCDF4')

    # Dimensions
    n_stations = 5
    n_times = 100
    max_name_len = 50

    ds.createDimension('time', n_times)
    ds.createDimension('station', n_stations)
    ds.createDimension('namelen', max_name_len)

    # Variables
    time_var = ds.createVariable('time', 'f8', ('time',))
    station_name_var = ds.createVariable('station_name', 'S1', ('station', 'namelen'))
    x_var = ds.createVariable('x', 'f4', ('station',))
    y_var = ds.createVariable('y', 'f4', ('station',))
    zeta_var = ds.createVariable('zeta', 'f4', ('time', 'station'))

    # Time data (100 hours starting from a reference)
    # Fort61Reader expects format without seconds
    base_time = datetime(2025, 1, 1)
    time_var.units = 'seconds since 2025-01-01 00:00'
    time_var[:] = np.arange(n_times) * 3600  # hourly data

    # Station names
    station_names = [
        'Test Station 1',
        'Test Station 2',
        'Magueyes Island, PR',  # Known good station
        'Test Station 4',
        'Test Station 5'
    ]

    for i, name in enumerate(station_names):
        name_padded = name.ljust(max_name_len)
        station_name_var[i, :] = list(name_padded)

    # Coordinates
    x_var[:] = [-75.0, -76.0, -67.0489, -78.0, -79.0]  # Longitude
    y_var[:] = [40.0, 39.0, 17.9700, 38.0, 37.0]      # Latitude

    # Water level data (simple sinusoidal for testing)
    for i in range(n_stations):
        zeta_var[:, i] = 0.5 * np.sin(np.arange(n_times) * 2 * np.pi / 24) + 0.3

    ds.close()

    return str(filepath)


@pytest.fixture
def mock_model_data():
    """Create mock model timeseries data"""
    time_index = pd.date_range(start='2025-01-01', periods=100, freq='h')
    data = 0.5 * np.sin(np.arange(100) * 2 * np.pi / 24) + 0.3

    df = pd.DataFrame({
        'water_level': data
    }, index=time_index)

    return df


@pytest.fixture
def mock_obs_data():
    """Create mock observation timeseries data"""
    time_index = pd.date_range(start='2025-01-01', periods=100, freq='h', tz='UTC')
    # Similar to model but with some noise and bias
    data = 0.5 * np.sin(np.arange(100) * 2 * np.pi / 24) + 0.25 + np.random.normal(0, 0.02, 100)

    df = pd.DataFrame({
        'water_level': data
    }, index=time_index)

    return df


@pytest.fixture
def mock_station_info():
    """Create mock station information dictionary"""
    return {
        'index': 2,
        'name': 'Magueyes Island, PR',
        'lon': -67.0489,
        'lat': 17.9700,
        'time_range': (datetime(2025, 1, 1), datetime(2025, 1, 5))
    }


@pytest.fixture
def mock_coops_match():
    """Create mock CO-OPS station match"""
    return {
        'name': 'Magueyes Island',
        'nos_id': '9759110',
        'distance': 0.0025,
        'state': 'PR',
        'lat': 17.970,
        'lon': -67.049
    }
