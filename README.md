# STOFS2D-OBS: STOFS2D Model Validation Package

[![CI](https://github.com/oceanmodeling/stofs2d-obs/actions/workflows/ci.yml/badge.svg)](https://github.com/oceanmodeling/stofs2d-obs/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compare STOFS2D model output with CO-OPS tide gauge observations. Automatically matches model stations to nearby CO-OPS gauges, fetches observations, and generates validation statistics and plots.

## Features

- Read STOFS2D fort.61.nc output files
- Automatic CO-OPS station matching using spatial search
- Fetch real-time tide gauge observations via searvey
- Statistical validation (RMSE, MAE, Bias, Correlation, Skill Score)
- Support for multiple datums (MSL, MLLW, NAVD88, STND)
- Generate comparison plots and reports
- Command-line interface and Python API
- Batch processing for multiple stations

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/oceanmodeling/stofs2d-obs.git
cd stofs2d-obs

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

### Requirements

- Python 3.9 or higher
- netCDF4, matplotlib, numpy, pandas
- searvey (for CO-OPS data)
- geopandas, shapely (for spatial operations)

All dependencies are automatically installed with the package.

## Quick Start

### Command Line Interface

The easiest way to get started is using the command-line tool:

```bash
# List available stations in your fort.61.nc file
stofs2d-compare fort.61.nc --list-stations

# Compare a single station and create a plot
stofs2d-compare fort.61.nc --station-idx 30 --plot comparison.png

# Save statistics to CSV
stofs2d-compare fort.61.nc --station-idx 30 --stats-file stats.csv

# Use a different datum
stofs2d-compare fort.61.nc --station-idx 30 --datum MLLW --plot output.png

# Batch process multiple stations
stofs2d-compare fort.61.nc --batch --max-stations 50 --summary-csv results.csv
```

**Note:** If `stofs2d-compare` is not in your PATH, use: `python3 -m stofs2d_obs.cli`

### Python API

```python
from searvey import fetch_coops_station
from stofs2d_obs import Fort61Reader, COOPSMatcher, ModelObsComparison

# Step 1: Read STOFS2D model output
fort61 = Fort61Reader('fort.61.nc')
station_info = fort61.get_station_info(30)  # Station index
model_data = fort61.get_station_data(30)

# Step 2: Find nearest CO-OPS station
matcher = COOPSMatcher(search_radius=0.5)  # 0.5 degrees (~55 km)
coops_match = matcher.get_best_match(station_info['lon'], station_info['lat'])

# Step 3: Fetch observation data
obs_data = fetch_coops_station(
    station_id=coops_match['nos_id'],
    start_date=station_info['time_range'][0],
    end_date=station_info['time_range'][1],
    product='water_level',
    datum='MSL',
)

# Step 4: Create comparison and generate outputs
comparison = ModelObsComparison(
    model_data=model_data,
    obs_data=obs_data,
    station_name=station_info['name'],
    model_name='STOFS2D',
    datum='MSL'
)

comparison.print_statistics()
comparison.plot_comparison(save_path='validation.png')

fort61.close()
```

See `examples/basic_comparison.py` for a complete working example.

## Command-Line Options

### Station Selection

| Option | Description |
|--------|-------------|
| `--station-idx N` | Process single station by index (0-based) |
| `--list-stations` | List available stations in the file |
| `--max-list N` | Limit station listing to first N stations |
| `--batch` | Process multiple stations automatically |
| `--station-range START END` | Process specific range of stations |

### Output Options

| Option | Description |
|--------|-------------|
| `--plot FILE` | Save comparison plot (PNG, PDF, or SVG) |
| `--stats-file FILE` | Save statistics (CSV or JSON) |
| `--summary-csv FILE` | Save batch summary to CSV (batch mode) |
| `--html-report FILE` | Generate HTML validation report (batch mode) |
| `--save-plots DIR` | Save individual plots to directory (batch mode) |

### Configuration

| Option | Description |
|--------|-------------|
| `--datum DATUM` | Vertical datum: MSL, MLLW, NAVD88, STND (default: MSL) |
| `--search-radius R` | CO-OPS search radius in degrees (default: 0.5) |
| `--max-stations N` | Maximum stations to process in batch mode |

### General

| Option | Description |
|--------|-------------|
| `--verbose, -v` | Show detailed progress information |
| `--quiet, -q` | Suppress output except errors |
| `--version` | Show version and exit |
| `--help, -h` | Show help message |

## Examples

### Single Station Comparison

```bash
# Basic comparison with plot
stofs2d-compare fort.61.nc --station-idx 30 --plot comparison.png

# Detailed output with statistics file
stofs2d-compare fort.61.nc --station-idx 30 \
    --plot comparison.png \
    --stats-file stats.csv \
    --verbose

# Use NAVD88 datum with larger search radius
stofs2d-compare fort.61.nc --station-idx 30 \
    --datum NAVD88 \
    --search-radius 1.0 \
    --plot output.png
```

### Batch Processing

```bash
# Process first 50 stations and save summary
stofs2d-compare fort.61.nc --batch --max-stations 50 --summary-csv results.csv

# Process specific station range with HTML report
stofs2d-compare fort.61.nc --station-range 0 100 \
    --summary-csv results.csv \
    --html-report validation.html

# Full batch processing with individual plots
stofs2d-compare fort.61.nc --batch --max-stations 100 \
    --summary-csv results.csv \
    --html-report validation.html \
    --save-plots output_plots/
```

### Python API - Batch Processing

```python
from stofs2d_obs import Fort61Reader, COOPSMatcher, ModelObsComparison
from searvey import fetch_coops_station
import pandas as pd

fort61 = Fort61Reader('fort.61.nc')
matcher = COOPSMatcher(search_radius=0.5)

results = []
for station_idx in range(50):  # Process first 50 stations
    try:
        # Get model data
        station_info = fort61.get_station_info(station_idx)
        model_data = fort61.get_station_data(station_idx)

        # Find CO-OPS match
        coops_match = matcher.get_best_match(
            station_info['lon'], station_info['lat']
        )
        if not coops_match:
            continue

        # Fetch observations
        obs_data = fetch_coops_station(
            station_id=coops_match['nos_id'],
            start_date=station_info['time_range'][0],
            end_date=station_info['time_range'][1],
            product='water_level',
            datum='MSL'
        )
        if len(obs_data) == 0:
            continue

        # Compare and collect statistics
        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name=station_info['name'],
            model_name='STOFS2D',
            datum='MSL'
        )

        stats = comparison.calculate_statistics()
        results.append({
            'station_idx': station_idx,
            'station_name': station_info['name'],
            'coops_id': coops_match['nos_id'],
            'rmse': stats['rmse'],
            'correlation': stats['correlation'],
            'n_points': stats['n_points']
        })

        # Save individual plot
        comparison.plot_comparison(f'station_{station_idx}.png')

    except Exception as e:
        print(f"Station {station_idx} failed: {e}")
        continue

# Save summary
df = pd.DataFrame(results)
df.to_csv('batch_results.csv', index=False)
print(f"Processed {len(results)} stations successfully")

fort61.close()
```

## Validation Statistics

The package calculates standard validation metrics:

| Statistic | Description | Units |
|-----------|-------------|-------|
| **RMSE** | Root Mean Square Error | meters |
| **MAE** | Mean Absolute Error | meters |
| **Bias** | Mean(model - obs) - systematic error | meters |
| **Correlation** | Pearson correlation coefficient | -1 to +1 |
| **Skill Score** | Murphy skill score (1=perfect, 0=no skill) | dimensionless |

## Supported Datums

- **MSL** - Mean Sea Level (default)
- **MLLW** - Mean Lower Low Water
- **NAVD88** - North American Vertical Datum 1988
- **STND** - Station Datum

Not all CO-OPS stations support all datums. If data is not available for the requested datum, try a different one or check the CO-OPS website for station capabilities.

## Troubleshooting

### "No CO-OPS stations found"

Increase the search radius:
```bash
stofs2d-compare fort.61.nc --station-idx 30 --search-radius 1.0
```

Or try a different station that's closer to the coast.

### "No observation data available"

The CO-OPS station may not support the requested datum, or data may not be available for the time period. Try:
- Different datum: `--datum MLLW`
- Check if the time range overlaps with available observations
- Verify the station is active on [NOAA Tides & Currents](https://tidesandcurrents.noaa.gov/)

### Command not found: stofs2d-compare

Use the module form:
```bash
python3 -m stofs2d_obs.cli fort.61.nc --station-idx 30
```

Or add `~/.local/bin` to your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs pytest, black, isort, flake8, mypy, and other development tools.

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stofs2d_obs --cov-report=html

# Run specific test file
pytest tests/test_comparison.py -v
```

### Code Formatting

```bash
# Format with black
black stofs2d_obs/

# Sort imports
isort stofs2d_obs/

# Check code style
flake8 stofs2d_obs/
```

### Type Checking

```bash
mypy stofs2d_obs/
```

## Package Structure

```
stofs2d_obs/
├── __init__.py         # Package exports
├── fort61.py           # Fort.61.nc file reader
├── observations.py     # CO-OPS station matching
├── comparison.py       # Model-obs comparison and statistics
└── cli.py              # Command-line interface

tests/                  # Unit tests
examples/               # Usage examples
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes with tests
4. Format code with black and isort
5. Run tests (`pytest`)
6. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Built on [searvey](https://github.com/oceanmodeling/searvey) for CO-OPS data access
- STOFS2D model developed by NOAA/NOS/OCS
- CO-OPS observations from [NOAA Tides & Currents](https://tidesandcurrents.noaa.gov/)

## Citation

If you use this package in your research, please cite:

```
STOFS2D-OBS: A Python package for validating STOFS2D model output
against CO-OPS tide gauge observations (2025).
```

## Related Projects

- [searvey](https://github.com/oceanmodeling/searvey) - Fetch ocean observations
- [ADCIRC](https://adcirc.org/) - Advanced circulation model for coastal waters
- [STOFS](https://tidesandcurrents.noaa.gov/stofs/) - NOAA Storm Surge and Tide Operational Forecast System

## Support

- Report issues: https://github.com/oceanmodeling/stofs2d-obs/issues
- Documentation: https://stofs2d-obs.readthedocs.io
- CO-OPS API: https://tidesandcurrents.noaa.gov/api/

---

**Version:** 0.1.0
**Status:** Alpha - Under active development
