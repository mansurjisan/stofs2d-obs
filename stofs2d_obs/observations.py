"""
CO-OPS Observation Station Matching
===================================

Module for finding and matching CO-OPS tide gauge stations to model locations
using the searvey package.
"""

import sys
import numpy as np
from searvey.coops import get_coops_stations


class COOPSMatcher:
    """Match STOFS2D stations to CO-OPS observation stations"""

    def __init__(self, search_radius=0.5):
        """
        Initialize matcher

        Parameters:
        -----------
        search_radius : float
            Search radius in degrees for finding nearby stations
        """
        self.search_radius = search_radius
        self.coops_stations = None
        self._load_coops_stations()

    def _load_coops_stations(self):
        """Load CO-OPS station metadata using searvey"""
        print("\nLoading CO-OPS station metadata...")
        try:
            self.coops_stations = get_coops_stations(metadata_source='main')
            print(f"Loaded {len(self.coops_stations)} CO-OPS stations")
        except Exception as e:
            print(f"Error loading CO-OPS stations: {e}", file=sys.stderr)
            raise

    def find_nearest(self, lon, lat, max_results=5):
        """
        Find nearest CO-OPS stations to given coordinates

        Parameters:
        -----------
        lon : float
            Longitude
        lat : float
            Latitude
        max_results : int
            Maximum number of results to return

        Returns:
        --------
        pandas.DataFrame : Nearest stations sorted by distance
        """
        # Calculate distances
        self.coops_stations['distance'] = np.sqrt(
            (self.coops_stations.geometry.x - lon)**2 +
            (self.coops_stations.geometry.y - lat)**2
        )

        # Filter by search radius and sort
        nearby = self.coops_stations[
            self.coops_stations['distance'] <= self.search_radius
        ].sort_values('distance').head(max_results)

        return nearby

    def get_best_match(self, lon, lat, require_valid_id=True):
        """
        Get the single best matching CO-OPS station

        Parameters:
        -----------
        lon : float
            Longitude
        lat : float
            Latitude
        require_valid_id : bool
            If True, only return stations with valid 7-digit CO-OPS IDs

        Returns:
        --------
        dict : Best matching station info or None
        """
        matches = self.find_nearest(lon, lat, max_results=10)

        if len(matches) == 0:
            print(f"Warning: No CO-OPS stations found within {self.search_radius} degrees of ({lon:.4f}, {lat:.4f})")
            return None

        # Filter for valid CO-OPS station IDs (7 digits) if required
        if require_valid_id:
            matches = matches[matches.index.astype(str).str.match(r'^\d{7}$')]
            if len(matches) == 0:
                print(f"Warning: No valid 7-digit CO-OPS stations found within {self.search_radius} degrees")
                return None

        match = matches.iloc[0]

        return {
            'nos_id': match.name,
            'name': match['name'],
            'lon': match.geometry.x,
            'lat': match.geometry.y,
            'distance': match['distance'],
            'status': match.get('status', 'unknown')
        }
