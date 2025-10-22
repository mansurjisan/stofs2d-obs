# How to Run the STOFS2D-Observation Comparison Script

## Quick Start (3 Steps)

### Step 1: Install Required Packages

```bash
# Install packages to system Python (if you don't have venv setup)
python3 -m pip install --break-system-packages netCDF4 matplotlib numpy searvey pandas geopandas pytz
```

**OR** if you have `python3-venv` installed:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install packages
pip install netCDF4 matplotlib numpy searvey pandas geopandas pytz
```

### Step 2: Navigate to the Script Directory

```bash
cd /mnt/c/Searvey_Fort61
```

### Step 3: Run the Script!

```bash
# Quick demo (uses station 30 - Magueyes Island, PR)
python3 stofs2d_demo_quick.py
```

**Output:**
- Plot saved as `stofs2d_comparison_demo.png`
- Statistics printed to console

---

## Detailed Instructions

### Prerequisites

1. **Python 3.8+** installed
 ```bash
 python3 --version
 ```

2. **fort.61.nc file** in the current directory
 ```bash
 ls -lh fort.61.nc
 ```

3. **Internet connection** (to fetch CO-OPS data)

---

## Method 1: Quick Demo (Easiest)

**File:** `stofs2d_demo_quick.py`

This script automatically processes **Station 30 (Magueyes Island, PR)** which is known to have valid CO-OPS data.

```bash
python3 stofs2d_demo_quick.py
```

**What it does:**
- Reads fort.61.nc station 30
- Fetches CO-OPS data from station 9759110
- Creates comparison plot
- Saves: `stofs2d_comparison_demo.png`

**Customize the station:**

Edit `stofs2d_demo_quick.py` and change:
```python
station_info = fort61.get_station_info(30) # Change 30 to any station index
```

And update the CO-OPS station ID:
```python
obs_data = fetch_coops_station(
 station_id='9759110', # Change to matching CO-OPS station
 ...
)
```

---

## Method 2: Full Prototype (Automatic Station Search)

**File:** `stofs2d_obs_prototype.py`

This script automatically searches through multiple stations to find one with valid CO-OPS data.

```bash
python3 stofs2d_obs_prototype.py
```

**What it does:**
- Tries stations: 0, 5, 10, 15, 20, 25, 30, ...
- For each station, finds nearest CO-OPS station
- Fetches observation data
- Uses first station with valid data
- Saves: `stofs2d_comparison_prototype.png`

**Customize which stations to try:**

Edit `stofs2d_obs_prototype.py` around line 500:
```python
STATION_INDICES_TO_TRY = [0, 5, 10, 20, 50, 100] # Your custom list
SEARCH_RADIUS = 0.5 # Increase if no CO-OPS stations nearby (in degrees)
```

---

## Method 3: Use as Python Module

Create your own script:

```python
from stofs2d_obs_prototype import Fort61Reader, COOPSMatcher, ModelObsComparison
from searvey._coops_api import fetch_coops_station

# 1. Read model data
fort61 = Fort61Reader('fort.61.nc')
station_info = fort61.get_station_info(30) # Change station index
model_data = fort61.get_station_data(30)

# 2. Find CO-OPS station
matcher = COOPSMatcher(search_radius=0.5)
coops_match = matcher.get_best_match(station_info['lon'], station_info['lat'])

# 3. Fetch observations
datum = 'MSL' # or 'MLLW', 'NAVD88', etc.
obs_data = fetch_coops_station(
 station_id=coops_match['nos_id'],
 start_date=station_info['time_range'][0],
 end_date=station_info['time_range'][1],
 product='water_level',
 datum=datum,
)

# 4. Create comparison
comparison = ModelObsComparison(
 model_data=model_data,
 obs_data=obs_data,
 station_name=station_info['name'],
 model_name='STOFS2D',
 datum=datum
)

# 5. Generate outputs
comparison.print_statistics()
comparison.plot_comparison(save_path='my_comparison.png')

fort61.close()
```

---

## Common Customizations

### Change the Station

```python
# Method 1: By index (0-based)
station_info = fort61.get_station_info(15) # Station 15
model_data = fort61.get_station_data(15)

# Method 2: List all stations first
fort61.list_stations(n=20) # Show first 20 stations
```

### Change the Datum

```python
datum = 'MLLW' # Mean Lower Low Water
# or
datum = 'NAVD88' # North American Vertical Datum 1988
# or
datum = 'STND' # Station Datum
```

### Change Output Filename

```python
comparison.plot_comparison(save_path='hurricane_validation.png')
```

### Change Search Radius for CO-OPS Stations

```python
matcher = COOPSMatcher(search_radius=1.0) # 1 degree (~111 km)
```

---

## Expected Output

### Console Output

```
======================================================================
STOFS2D Quick Demo - Station 30
======================================================================

Reading model data...
Loaded fort.61.nc file:
 Stations: 2740
 Time steps: 1680
 Time range: 2025-10-21 00:06:00 to 2025-10-28 00:00:00
Station: ID: 9759110.0 , Magueyes island,pr
Location: (-67.0489, 17.9700)
Model data points: 1680

Fetching CO-OPS data for station 9759110...
Observation data points: 337

Creating comparison...

Data alignment:
 Model points: 1680
 Observation points: 337
 Aligned points: 337

============================================================
Validation Statistics: Magueyes Island, PR
============================================================
Data points: 337

Error Metrics:
 RMSE: 0.1948 m
 MAE: 0.1919 m
 Bias: +0.1919 m
 Correlation: 0.8767
 Skill Score: -6.8918
...
============================================================

Generating plot...
Plot saved to: stofs2d_comparison_demo.png

======================================================================
Demo complete! Check stofs2d_comparison_demo.png
======================================================================
```

### Plot File

- **Filename:** `stofs2d_comparison_demo.png` (or your custom name)
- **Location:** Same directory as the script
- **Size:** ~300 KB
- **Format:** PNG, 150 DPI

---

## Troubleshooting

### Problem: "No module named 'netCDF4'"

**Solution:** Install required packages
```bash
python3 -m pip install --break-system-packages netCDF4 matplotlib numpy searvey pandas geopandas
```

### Problem: "No CO-OPS stations found"

**Solutions:**
1. Increase search radius:
 ```python
 matcher = COOPSMatcher(search_radius=1.5) # Try larger radius
 ```

2. Try a different station:
 ```python
 station_info = fort61.get_station_info(50) # Try different index
 ```

3. Check if station is coastal:
 ```python
 fort61.list_stations(n=20) # Look for coastal stations
 ```

### Problem: "No observation data available"

**Causes:**
- Station doesn't support requested datum (MSL, MLLW, etc.)
- Time range in fort.61.nc doesn't have CO-OPS data
- Station is discontinued

**Solutions:**
1. Try different datum:
 ```python
 datum = 'MLLW' # Instead of 'MSL'
 ```

2. Use the full prototype (it tries multiple datums automatically):
 ```bash
 python3 stofs2d_obs_prototype.py
 ```

### Problem: "RuntimeError: NetCDF: Not a valid ID"

This is a harmless cleanup warning. Ignore it. The script still works correctly.

### Problem: Timezone errors

The script automatically handles timezone differences between model and observation data. If you see timezone errors, ensure your pandas and numpy are up to date:
```bash
pip install --upgrade pandas numpy
```

---

## Batch Processing Multiple Stations

Create a script to process multiple stations:

```python
from stofs2d_obs_prototype import Fort61Reader, COOPSMatcher, ModelObsComparison
from searvey._coops_api import fetch_coops_station

fort61 = Fort61Reader('fort.61.nc')
matcher = COOPSMatcher(search_radius=0.5)

# Process stations 0, 10, 20, 30, 40
for station_idx in [0, 10, 20, 30, 40]:
 try:
 print(f"\n{'='*60}")
 print(f"Processing station {station_idx}...")

 # Get model data
 station_info = fort61.get_station_info(station_idx)
 model_data = fort61.get_station_data(station_idx)

 # Find CO-OPS match
 coops_match = matcher.get_best_match(
 station_info['lon'],
 station_info['lat']
 )

 if not coops_match:
 print(f" No CO-OPS station found, skipping...")
 continue

 # Fetch observations
 obs_data = fetch_coops_station(
 station_id=coops_match['nos_id'],
 start_date=station_info['time_range'][0],
 end_date=station_info['time_range'][1],
 product='water_level',
 datum='MSL',
 )

 if len(obs_data) == 0:
 print(f" No observation data, skipping...")
 continue

 # Create comparison
 comparison = ModelObsComparison(
 model_data=model_data,
 obs_data=obs_data,
 station_name=station_info['name'],
 model_name='STOFS2D',
 datum='MSL'
 )

 # Save plot with unique name
 comparison.plot_comparison(
 save_path=f'comparison_station_{station_idx}.png'
 )

 print(f" Success! Plot saved.")

 except Exception as e:
 print(f" Error: {e}")
 continue

fort61.close()
print("\n" + "="*60)
print("Batch processing complete!")
```

Save as `batch_process.py` and run:
```bash
python3 batch_process.py
```

---

## File Locations

All files are in: `/mnt/c/Searvey_Fort61/`

| File | Purpose |
|------|---------|
| `stofs2d_demo_quick.py` | Quick demo (station 30) |
| `stofs2d_obs_prototype.py` | Full prototype (auto-search) |
| `fort.61.nc` | Your STOFS2D model output |
| `requirements_prototype.txt` | List of dependencies |
| `PROTOTYPE_README.md` | Detailed documentation |
| `QUICK_REFERENCE.md` | Code examples |

---

## Getting Help

1. **Check documentation:**
 ```bash
 cat PROTOTYPE_README.md
 cat QUICK_REFERENCE.md
 ```

2. **List available stations:**
 ```python
 from stofs2d_obs_prototype import Fort61Reader
 fort61 = Fort61Reader('fort.61.nc')
 fort61.list_stations(n=50) # Show 50 stations
 ```

3. **Check CO-OPS stations nearby:**
 ```python
 from stofs2d_obs_prototype import COOPSMatcher
 matcher = COOPSMatcher(search_radius=1.0)
 nearby = matcher.find_nearest(lon=-75.5, lat=35.2, max_results=5)
 print(nearby)
 ```

---

## Summary

**Easiest way to run:**
```bash
cd /mnt/c/Searvey_Fort61
python3 stofs2d_demo_quick.py
```

**To customize:**
- Edit station index in the script
- Change datum (MSL, MLLW, NAVD88)
- Adjust search radius for CO-OPS stations

**Output:**
- PNG plot file
- Statistics in console

That's it! You're ready to validate your STOFS2D model output against CO-OPS observations! 
