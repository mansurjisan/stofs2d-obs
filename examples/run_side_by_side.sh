#!/bin/bash
# Create side-by-side comparison plots

# Configuration
START_STATION=0
END_STATION=500
DATUM="MSL"
OUTPUT_DIR="comparison_plots"

# Set matplotlib backend
export MPLBACKEND=Agg

echo "========================================================================"
echo "Side-by-Side Comparison: Anomaly vs NoAnomaly"
echo "========================================================================"
echo "Stations: $START_STATION to $END_STATION"
echo "Datum: $DATUM"
echo "Output: $OUTPUT_DIR/"
echo ""

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate stofs2d-obs

# Run the script
python compare_side_by_side.py \
    --station-range $START_STATION $END_STATION \
    --datum $DATUM \
    --output-dir $OUTPUT_DIR

echo ""
echo "========================================================================"
echo "✓ Complete! View plots in: $OUTPUT_DIR/"
echo "========================================================================"
