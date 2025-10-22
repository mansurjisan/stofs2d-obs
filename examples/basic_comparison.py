#!/usr/bin/env python3
"""
Basic STOFS2D-Observation Comparison Example
============================================

This example demonstrates how to use the stofs2d_obs package
to compare model output with CO-OPS observations.
"""

from stofs2d_obs import Fort61Reader, COOPSMatcher, ModelObsComparison
from searvey._coops_api import fetch_coops_station


def main():
    print("="*70)
    print("STOFS2D-OBS Basic Comparison Example")
    print("="*70)

    # Configuration
    FORT61_FILE = '../fort.61.nc'  # Adjust path as needed
    STATION_INDEX = 30  # Magueyes Island, PR
    DATUM = 'MSL'

    # Step 1: Read STOFS2D model data
    print("\n[1/5] Reading STOFS2D model output...")
    with Fort61Reader(FORT61_FILE) as fort61:
        # Get station information
        station_info = fort61.get_station_info(STATION_INDEX)
        print(f"  Station: {station_info['name']}")
        print(f"  Location: ({station_info['lon']:.4f}, {station_info['lat']:.4f})")

        # Extract model timeseries
        model_data = fort61.get_station_data(STATION_INDEX)
        print(f"  Model data points: {len(model_data)}")

        # Step 2: Find matching CO-OPS station
        print(f"\n[2/5] Finding nearest CO-OPS station...")
        matcher = COOPSMatcher(search_radius=0.5)
        coops_match = matcher.get_best_match(station_info['lon'], station_info['lat'])

        if coops_match is None:
            print("  ERROR: No CO-OPS station found")
            return

        print(f"  CO-OPS Station: {coops_match['name']} (ID: {coops_match['nos_id']})")
        print(f"  Distance: {coops_match['distance']:.4f} degrees (~{coops_match['distance']*111:.1f} km)")

        # Step 3: Fetch CO-OPS observation data
        print(f"\n[3/5] Fetching CO-OPS observation data...")
        obs_data = fetch_coops_station(
            station_id=coops_match['nos_id'],
            start_date=station_info['time_range'][0],
            end_date=station_info['time_range'][1],
            product='water_level',
            datum=DATUM,
        )
        print(f"  Observation data points: {len(obs_data)}")

        if len(obs_data) == 0:
            print("  ERROR: No observation data available")
            return

        # Step 4: Create comparison
        print(f"\n[4/5] Creating model-observation comparison...")
        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name=f"{station_info['name']} / {coops_match['name']}",
            model_name='STOFS2D',
            datum=DATUM
        )

        # Print statistics
        comparison.print_statistics()

        # Step 5: Generate plot
        print(f"[5/5] Generating comparison plot...")
        output_file = 'stofs2d_comparison_example.png'
        comparison.plot_comparison(save_path=output_file)

    print("\n" + "="*70)
    print("Example complete!")
    print(f"Plot saved to: {output_file}")
    print("="*70)


if __name__ == '__main__':
    main()
