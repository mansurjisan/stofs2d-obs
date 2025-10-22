"""
STOFS2D Observation Comparison Package
======================================

A Python package for comparing STOFS2D model output (fort.61.nc) with
CO-OPS tide gauge observations using the searvey package.

Main Components:
    - Fort61Reader: Read and extract STOFS2D model data
    - COOPSMatcher: Find and match CO-OPS observation stations
    - ModelObsComparison: Compare model vs observations with statistics and plots

Example:
    >>> from stofs2d_obs import Fort61Reader, COOPSMatcher, ModelObsComparison
    >>>
    >>> # Read model data
    >>> fort61 = Fort61Reader('fort.61.nc')
    >>> model_data = fort61.get_station_data(0)
    >>>
    >>> # Find CO-OPS station
    >>> matcher = COOPSMatcher()
    >>> coops_match = matcher.get_best_match(lon=-75.5, lat=35.2)
    >>>
    >>> # Compare
    >>> comparison = ModelObsComparison(model_data, obs_data, 'Station Name')
    >>> comparison.plot_comparison('output.png')
"""

__version__ = "0.1.0"
__author__ = "STOFS2D Validation Team"
__license__ = "MIT"

from stofs2d_obs.comparison import ModelObsComparison
from stofs2d_obs.fort61 import Fort61Reader
from stofs2d_obs.observations import COOPSMatcher

__all__ = [
    "Fort61Reader",
    "COOPSMatcher",
    "ModelObsComparison",
    "__version__",
]
