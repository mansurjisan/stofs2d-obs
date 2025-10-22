# STOFS2D-OBS: STOFS2D Model Validation Package

[![CI](https://github.com/oceanmodeling/stofs2d-obs/actions/workflows/ci.yml/badge.svg)](https://github.com/oceanmodeling/stofs2d-obs/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/oceanmodeling/stofs2d-obs/branch/main/graph/badge.svg)](https://codecov.io/gh/oceanmodeling/stofs2d-obs)
[![PyPI version](https://badge.fury.io/py/stofs2d-obs.svg)](https://badge.fury.io/py/stofs2d-obs)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compare STOFS output with CO-OPS tide gauge observations.

## Features

- **Read STOFS2D fort.61.nc output** - Extract model timeseries data
- **Fetch CO-OPS observations** - Automatic retrieval via searvey package
- **Station matching** - Find nearest CO-OPS stations to model locations
- **Statistical validation** - RMSE, MAE, Bias, Correlation, Skill Score
- **Multiple datums** - Support for MSL, MLLW, NAVD88, STND

## Installation

### From source

```bash
# Clone or download this repository
cd stofs2d-obs

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Requirements

- Python 3.9+
- netCDF4
- matplotlib
- numpy
- pandas
- searvey
- geopandas

## Quick Start

### Python API

```python
from searvey import fetch_coops_station

from stofs2d_obs import Fort61Reader, COOPSMatcher, ModelObsComparison

# Read STOFS2D model output
fort61 = Fort61Reader('fort.61.nc')
station_info = fort61.get_station_info(0)
model_data = fort61.get_station_data(0)

# Find nearest CO-OPS station
matcher = COOPSMatcher(search_radius=0.5)
coops_match = matcher.get_best_match(station_info['lon'], station_info['lat'])

# Fetch observations
obs_data = fetch_coops_station(
 station_id=coops_match['nos_id'],
 start_date=station_info['time_range'][0],
 end_date=station_info['time_range'][1],
 product='water_level',
 datum='MSL',
)

# Create comparison
comparison = ModelObsComparison(
 model_data=model_data,
 obs_data=obs_data,
 station_name=station_info['name'],
 model_name='STOFS2D',
 datum='MSL'
)

# Generate outputs
comparison.print_statistics()
comparison.plot_comparison(save_path='validation.png')

fort61.close()
```

### Command Line

#### Single Station Comparison

```bash
# List available stations
stofs2d-compare fort.61.nc --list-stations

# Compare single station and generate plot
stofs2d-compare fort.61.nc --station-idx 30 --plot comparison.png

# Save statistics to CSV file
stofs2d-compare fort.61.nc --station-idx 30 --stats-file stats.csv

# Use different datum and search radius
stofs2d-compare fort.61.nc --station-idx 30 --datum MLLW --search-radius 1.0

# Combine plot and stats with verbose output
stofs2d-compare fort.61.nc --station-idx 30 --plot output.png --stats-file stats.csv --verbose

# Quiet mode (only errors)
stofs2d-compare fort.61.nc --station-idx 30 --plot output.png --quiet
```

#### Batch Processing

```bash
# Process first 50 stations
stofs2d-compare fort.61.nc --batch --max-stations 50 --summary-csv results.csv

# Process specific station range
stofs2d-compare fort.61.nc --station-range 0 100 --summary-csv results.csv

# Generate HTML validation report
stofs2d-compare fort.61.nc --station-range 0 100 --html-report validation.html

# Full batch validation with plots
stofs2d-compare fort.61.nc --batch --max-stations 100 \
 --summary-csv results.csv \
 --html-report validation.html \
 --save-plots output_plots/

# Process all stations (WARNING: may take a long time!)
stofs2d-compare fort.61.nc --batch --summary-csv all_stations.csv
```

**Note:** If `stofs2d-compare` is not in your PATH, use: `python3 -m stofs2d_obs.cli`

#### CLI Options

**Station Selection (mutually exclusive):**

| Option | Description |
|--------|-------------|
| `--station-idx N` | Process single station by index (0-based) |
| `--list-stations` | List available stations and exit |
| `--batch` | Batch process multiple stations |
| `--station-range START END` | Process station range (inclusive) |

**Batch Processing Options:**

| Option | Description |
|--------|-------------|
| `--max-stations N` | Maximum number of stations (with --batch) |
| `--summary-csv FILE` | Save batch summary to CSV |
| `--html-report FILE` | Generate HTML validation report |
| `--save-plots DIR` | Save plots to directory |

**Single Station Output:**

| Option | Description |
|--------|-------------|
| `--plot FILE` | Save comparison plot (PNG, PDF, SVG) |
| `--stats-file FILE` | Save statistics (CSV or JSON) |

**General Options:**

| Option | Description |
|--------|-------------|
| `nc_file` | Path to fort.61.nc file (required) |
| `--datum DATUM` | Vertical datum (MSL, MLLW, NAVD88, STND) - default: MSL |
| `--search-radius R` | CO-OPS search radius in degrees - default: 0.5 |
| `--verbose, -v` | Verbose output |
| `--quiet, -q` | Minimal output (only errors) |
| `--version` | Show version and exit |
| `--help, -h` | Show help message |

## Package Structure

```
stofs2d_obs/
├── __init__.py # Package initialization
├── fort61.py # STOFS2D fort.61.nc reader
├── observations.py # CO-OPS station matching
├── comparison.py # Model-observation comparison
└── cli.py # Command-line interface
```

## Classes

### Fort61Reader

Read and extract data from STOFS2D fort.61.nc files.

**Methods:**
- `get_station_info(station_idx)` - Get station metadata
- `get_station_data(station_idx)` - Extract timeseries data
- `list_stations(n)` - List available stations

### COOPSMatcher

Find CO-OPS observation stations near model locations.

**Methods:**
- `find_nearest(lon, lat, max_results)` - Find nearby stations
- `get_best_match(lon, lat)` - Get closest valid station

### ModelObsComparison

Compare model and observation data with statistics and visualization.

**Methods:**
- `calculate_statistics()` - Compute validation metrics
- `print_statistics()` - Display formatted results
- `plot_comparison(save_path)` - Generate comparison plots

## Validation Statistics

The package calculates standard validation metrics:

| Statistic | Description |
|-----------|-------------|
| **RMSE** | Root Mean Square Error (m) |
| **MAE** | Mean Absolute Error (m) |
| **Bias** | Systematic error: mean(model - obs) (m) |
| **Correlation** | Pearson correlation coefficient |
| **Skill Score** | Murphy skill score (1=perfect, 0=no skill) |

## Supported Datums

- **MSL** - Mean Sea Level
- **MLLW** - Mean Lower Low Water
- **NAVD88** - North American Vertical Datum 1988
- **STND** - Station Datum

## Examples

See the `examples/` directory for:
- `basic_comparison.py` - Simple single-station comparison using Python API

For CLI examples, run:
```bash
stofs2d-compare --help
```

## Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Format code

```bash
black stofs2d_obs/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Citation

If you use this package in your research, please cite:

```
STOFS2D-OBS: A Python package for validating STOFS2D model output
against CO-OPS tide gauge observations (2025).
```

## Acknowledgments

- Built on [searvey](https://github.com/oceanmodeling/searvey) for CO-OPS data access
- STOFS2D model by NOAA/NOS
- CO-OPS observations from NOAA Tides & Currents

## Contact

For questions or issues, please open an issue on GitHub.

## Related Projects

- [searvey](https://github.com/oceanmodeling/searvey) - Fetch ocean observations
- [ADCIRC](https://adcirc.org/) - Advanced circulation model
- [STOFS](https://tidesandcurrents.noaa.gov/stofs/) - NOAA Storm Surge and Tide Operational Forecast System

---

**Version:** 0.1.0
**Status:** Alpha - Under active development
