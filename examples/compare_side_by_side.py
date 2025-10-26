#!/usr/bin/env python3
"""
Create side-by-side comparison plots of anomaly vs noanomaly
Without the difference panel - uses ModelObsComparison class
"""
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set backend before importing stofs2d_obs
import matplotlib
matplotlib.use('Agg')

from stofs2d_obs import Fort61Reader, ModelObsComparison
from stofs2d_obs.observations import COOPSMatcher
from searvey import fetch_coops_station

def create_side_by_side_plot(station_idx, datum='MSL', output_dir='comparison_plots'):
    """
    Create side-by-side comparison plot for a single station
    """
    files = {
        'WITH Anomaly': 'stofs_2d_glo.t00z.points.autoval.cwl.nc',
        'WITHOUT Anomaly': 'stofs_2d_glo.t00z.points.autoval.cwl.noanomaly.nc'
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"Processing Station {station_idx}")
    print('='*80)
    
    # Read station info from first file
    reader1 = Fort61Reader(files['WITH Anomaly'])
    station_info = reader1.get_station_info(station_idx)
    print(f"Station: {station_info['name']}")
    print(f"Location: ({station_info['lon']:.4f}, {station_info['lat']:.4f})")
    
    # Find CO-OPS station
    matcher = COOPSMatcher()
    coops_match = matcher.get_best_match(station_info['lon'], station_info['lat'])
    
    if not coops_match:
        print(f"✗ No CO-OPS station found")
        reader1.close()
        return False
    
    print(f"CO-OPS: {coops_match['name']} (ID: {coops_match['nos_id']})")
    
    # Fetch observation data
    try:
        obs_data = fetch_coops_station(
            station_id=coops_match['nos_id'],
            start_date=station_info['time_range'][0],
            end_date=station_info['time_range'][1],
            product='water_level',
            datum=datum,
        )
    except:
        # Try MSL if requested datum fails
        obs_data = fetch_coops_station(
            station_id=coops_match['nos_id'],
            start_date=station_info['time_range'][0],
            end_date=station_info['time_range'][1],
            product='water_level',
            datum='MSL',
        )
        datum = 'MSL'
    
    if len(obs_data) == 0:
        print(f"✗ No observation data")
        reader1.close()
        return False
    
    # Read model data from both files and create comparisons
    model_data1 = reader1.get_station_data(station_idx)
    reader1.close()
    
    reader2 = Fort61Reader(files['WITHOUT Anomaly'])
    model_data2 = reader2.get_station_data(station_idx)
    reader2.close()
    
    # Create comparison objects (they handle data alignment and stats)
    comp1 = ModelObsComparison(model_data1, obs_data, station_info['name'], "STOFS2D", datum)
    comp2 = ModelObsComparison(model_data2, obs_data, station_info['name'], "STOFS2D", datum)
    
    stats1 = comp1.calculate_statistics()
    stats2 = comp2.calculate_statistics()
    
    if len(comp1.aligned) == 0 or len(comp2.aligned) == 0:
        print(f"✗ No aligned data")
        return False
    
    # Create side-by-side plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
    
    # Plot 1: WITH Anomaly
    ax1.plot(
        model_data1.index,
        model_data1['water_level'],
        'b-',
        linewidth=1.5,
        label='STOFS2D Model',
        alpha=0.8
    )
    ax1.plot(
        comp1.obs_data.index,
        comp1.obs_data['obs_water_level'],
        'r-',
        linewidth=1.5,
        label='CO-OPS Observation',
        alpha=0.8
    )
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_ylabel(f'Water Level (m, {datum})', fontsize=11)
    ax1.set_xlabel('Date/Time', fontsize=11)
    ax1.set_title('WITH Anomaly', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=9)
    
    # Add stats box
    if stats1:
        stats_text = f"RMSE: {stats1['rmse']:.3f} m\nCorr: {stats1['correlation']:.3f}\nN: {stats1['n_points']}"
        ax1.text(
            0.02, 0.98,
            stats_text,
            transform=ax1.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        )
    
    # Plot 2: WITHOUT Anomaly
    ax2.plot(
        model_data2.index,
        model_data2['water_level'],
        'b-',
        linewidth=1.5,
        label='STOFS2D Model',
        alpha=0.8
    )
    ax2.plot(
        comp2.obs_data.index,
        comp2.obs_data['obs_water_level'],
        'r-',
        linewidth=1.5,
        label='CO-OPS Observation',
        alpha=0.8
    )
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_ylabel(f'Water Level (m, {datum})', fontsize=11)
    ax2.set_xlabel('Date/Time', fontsize=11)
    ax2.set_title('WITHOUT Anomaly', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9)
    
    # Add stats box
    if stats2:
        stats_text = f"RMSE: {stats2['rmse']:.3f} m\nCorr: {stats2['correlation']:.3f}\nN: {stats2['n_points']}"
        ax2.text(
            0.02, 0.98,
            stats_text,
            transform=ax2.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        )
    
    # Format dates for both axes
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Overall title
    fig.suptitle(
        f'{station_info["name"]} / {coops_match["name"]}',
        fontsize=14,
        fontweight='bold',
        y=1.02
    )
    
    plt.tight_layout()
    
    # Save plot
    plot_file = f'{output_dir}/station_{station_idx:04d}_comparison.png'
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {plot_file}")
    print(f"  WITH Anomaly:    RMSE={stats1['rmse']:.3f}m")
    print(f"  WITHOUT Anomaly: RMSE={stats2['rmse']:.3f}m")
    
    return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Create side-by-side comparison plots')
    parser.add_argument('--station-range', nargs=2, type=int, metavar=('START', 'END'),
                        help='Range of stations to process')
    parser.add_argument('--station-idx', type=int, help='Single station index')
    parser.add_argument('--datum', default='MSL', help='Vertical datum')
    parser.add_argument('--output-dir', default='comparison_plots', help='Output directory')
    
    args = parser.parse_args()
    
    if args.station_idx is not None:
        stations = [args.station_idx]
    elif args.station_range:
        stations = range(args.station_range[0], args.station_range[1])
    else:
        print("Error: Must specify either --station-idx or --station-range")
        sys.exit(1)
    
    print("="*80)
    print("Side-by-Side Comparison: Anomaly vs NoAnomaly")
    print("="*80)
    print(f"Datum: {args.datum}")
    print(f"Output: {args.output_dir}/")
    print(f"Stations: {len(stations)}")
    
    success = 0
    for idx in stations:
        try:
            if create_side_by_side_plot(idx, args.datum, args.output_dir):
                success += 1
        except Exception as e:
            print(f"✗ Error processing station {idx}: {e}")
    
    print(f"\n{'='*80}")
    print(f"✓ Completed: {success}/{len(stations)} stations")
    print(f"✓ Plots saved to: {args.output_dir}/")
    print("="*80)
