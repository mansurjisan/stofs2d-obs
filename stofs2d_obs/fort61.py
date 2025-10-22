"""
Fort.61 NetCDF File Reader
==========================

Module for reading and extracting STOFS2D model output from fort.61.nc files.
"""

import sys
import netCDF4 as nc
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class Fort61Reader:
    """Read and extract data from STOFS2D fort.61.nc files"""

    def __init__(self, nc_file):
        """
        Initialize reader with fort.61.nc file

        Parameters:
        -----------
        nc_file : str
            Path to fort.61.nc file
        """
        self.nc_file = nc_file
        self.ds = None
        self._open_file()

    def _open_file(self):
        """Open NetCDF file and cache metadata"""
        try:
            self.ds = nc.Dataset(self.nc_file, 'r')

            # Get time information
            time_var = self.ds.variables['time']
            time_units = time_var.units
            base_date_str = time_units.split('since ')[-1]
            self.base_date = datetime.strptime(base_date_str, '%Y-%m-%d %H:%M')

            # Convert time to datetime
            time_seconds = time_var[:]
            self.datetimes = [self.base_date + timedelta(seconds=float(t))
                             for t in time_seconds]

            # Get station metadata
            self.station_names_var = self.ds.variables['station_name']
            self.x_var = self.ds.variables['x']
            self.y_var = self.ds.variables['y']
            self.zeta_var = self.ds.variables['zeta']

            self.n_stations = len(self.station_names_var)
            self.n_times = len(self.datetimes)

            print(f"Loaded fort.61.nc file:")
            print(f"  Stations: {self.n_stations}")
            print(f"  Time steps: {self.n_times}")
            print(f"  Time range: {self.datetimes[0]} to {self.datetimes[-1]}")

        except Exception as e:
            print(f"Error opening file: {e}", file=sys.stderr)
            raise

    def get_station_info(self, station_idx):
        """
        Get metadata for a specific station

        Parameters:
        -----------
        station_idx : int
            Station index (0-based)

        Returns:
        --------
        dict : Station information
        """
        if station_idx >= self.n_stations:
            raise ValueError(f"Station index {station_idx} out of range (max: {self.n_stations-1})")

        name = ''.join(c.decode('utf-8') if isinstance(c, bytes) else c
                      for c in self.station_names_var[station_idx]).strip()

        return {
            'index': station_idx,
            'name': name,
            'lon': float(self.x_var[station_idx]),
            'lat': float(self.y_var[station_idx]),
            'time_range': (self.datetimes[0], self.datetimes[-1])
        }

    def get_station_data(self, station_idx):
        """
        Extract timeseries data for a specific station

        Parameters:
        -----------
        station_idx : int
            Station index (0-based)

        Returns:
        --------
        pandas.DataFrame : Timeseries data with columns ['time', 'water_level']
        """
        # Get water elevation data
        zeta_values = self.zeta_var[:, station_idx]

        # Filter out fill values
        valid_mask = ~np.isclose(zeta_values, -99999.0)
        valid_times = np.array(self.datetimes)[valid_mask]
        valid_zeta = zeta_values[valid_mask]

        # Create DataFrame
        df = pd.DataFrame({
            'time': valid_times,
            'water_level': valid_zeta
        })
        df.set_index('time', inplace=True)

        return df

    def list_stations(self, n=10):
        """
        List first n stations

        Parameters:
        -----------
        n : int
            Number of stations to list
        """
        print(f"\nFirst {n} stations:")
        print(f"{'Index':<8} {'Name':<30} {'Lon':<12} {'Lat':<12}")
        print("-" * 70)
        for i in range(min(n, self.n_stations)):
            info = self.get_station_info(i)
            print(f"{info['index']:<8} {info['name']:<30} {info['lon']:<12.6f} {info['lat']:<12.6f}")

    def close(self):
        """Close NetCDF file"""
        if self.ds:
            try:
                self.ds.close()
            except:
                pass  # Ignore errors on close

    def __del__(self):
        """Ensure file is closed"""
        self.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
