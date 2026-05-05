#!/usr/bin/env python3
"""
Two-panel comparison of two fort.61 model runs + CO-OPS observation.

Top panel:    Model A, Model B, CO-OPS observation overlaid (3 lines, 1 axis)
Bottom panel: (Model B - Model A) difference with red/blue fill ("Higher"/"Lower")

This extends the layout produced by extract_fort61.py --overlay by adding the
CO-OPS observation as a third line on the top panel, plus per-model RMSE/Corr
vs observation in the stats box.
"""
import os

# Cap BLAS thread counts before numpy is imported.
# searvey fetches CO-OPS metadata in parallel; on HPC clusters with low
# RLIMIT_NPROC (e.g. WCOSS2's 1024), each worker spawning 64 OpenBLAS
# threads exhausts the per-user process limit and the parallel fetch
# fails with "All objects passed were None".
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from stofs2d_obs import Fort61Reader, ModelObsComparison
from stofs2d_obs.observations import COOPSMatcher
from searvey import fetch_coops_station


def create_plot(file_a, file_b, station_idx, datum='MSL',
                output_dir='comparison_plots',
                label_a='Run A', label_b='Run B',
                search_radius=0.01):
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"Processing Station {station_idx}")
    print('='*80)

    # ---- Read run A ----
    reader_a = Fort61Reader(file_a)
    info_a = reader_a.get_station_info(station_idx)
    print(f"Station: {info_a['name']}")
    print(f"Location: ({info_a['lon']:.4f}, {info_a['lat']:.4f})")
    data_a = reader_a.get_station_data(station_idx)
    reader_a.close()

    # ---- CO-OPS match ----
    matcher = COOPSMatcher(search_radius=search_radius)
    coops_match = matcher.get_best_match(info_a['lon'], info_a['lat'])
    if not coops_match:
        print("X No CO-OPS station found")
        return None
    print(f"CO-OPS: {coops_match['name']} (ID: {coops_match['nos_id']})")

    # ---- Read run B (match by station name) ----
    reader_b = Fort61Reader(file_b)
    found_idx = None
    for i in range(reader_b.n_stations):
        if reader_b.get_station_info(i)['name'] == info_a['name']:
            found_idx = i
            break
    if found_idx is None:
        print("X Station not found in file B")
        reader_b.close()
        return None
    info_b = reader_b.get_station_info(found_idx)
    data_b = reader_b.get_station_data(found_idx)
    reader_b.close()

    # ---- Fetch observation ----
    obs_start = min(info_a['time_range'][0], info_b['time_range'][0])
    obs_end   = max(info_a['time_range'][1], info_b['time_range'][1])
    try:
        obs_data = fetch_coops_station(
            station_id=coops_match['nos_id'],
            start_date=obs_start, end_date=obs_end,
            product='water_level', datum=datum,
        )
    except Exception:
        try:
            obs_data = fetch_coops_station(
                station_id=coops_match['nos_id'],
                start_date=obs_start, end_date=obs_end,
                product='water_level', datum='MSL',
            )
            datum = 'MSL'
        except Exception as e:
            print(f"X Error fetching observations: {e}")
            return None
    if obs_data is None or len(obs_data) == 0:
        print("X No observation data")
        return None

    comp_a = ModelObsComparison(data_a, obs_data, info_a['name'], 'STOFS2D', datum)
    comp_b = ModelObsComparison(data_b, obs_data, info_a['name'], 'STOFS2D', datum)
    stats_a = comp_a.calculate_statistics()
    stats_b = comp_b.calculate_statistics()

    # ---- Difference (B - A) on common time index ----
    common_idx = data_a.index.intersection(data_b.index)
    a_common = data_a.loc[common_idx, 'water_level']
    b_common = data_b.loc[common_idx, 'water_level']
    diff = (b_common - a_common).values
    diff_times = common_idx

    # ---- Figure ----
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top: 2 models + obs
    ax1.plot(data_a.index, data_a['water_level'], 'b-', linewidth=1.5,
             label=f'STOFS2D - {label_a}', alpha=0.85)
    ax1.plot(data_b.index, data_b['water_level'], 'r-', linewidth=1.5,
             label=f'STOFS2D - {label_b}', alpha=0.85)
    ax1.plot(comp_a.obs_data.index, comp_a.obs_data['obs_water_level'],
             'k-', linewidth=1.2, label='CO-OPS Observation', alpha=0.7)
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_ylabel(f'Water Elevation (m, {datum})', fontsize=11)
    ax1.set_title(f"{info_a['name']}  |  CO-OPS {coops_match['nos_id']}",
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)

    stats_text = (
        f"{label_a} vs Obs:  RMSE={stats_a['rmse']:.3f} m,  Corr={stats_a['correlation']:.3f}\n"
        f"{label_b} vs Obs:  RMSE={stats_b['rmse']:.3f} m,  Corr={stats_b['correlation']:.3f}"
    )
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    # Bottom: difference (B - A) with red/blue fill
    ax2.plot(diff_times, diff, 'k-', linewidth=1.2,
             label=f'{label_b} - {label_a}')
    ax2.fill_between(diff_times, diff, 0, where=(diff >= 0),
                     color='red', alpha=0.3, label='Higher')
    ax2.fill_between(diff_times, diff, 0, where=(diff < 0),
                     color='blue', alpha=0.3, label='Lower')
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_ylabel('Elevation Difference (m)', fontsize=11)
    ax2.set_xlabel('Date/Time', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=10, framealpha=0.9)

    diff_stats = (
        f"Max Diff: {np.max(diff):.3f} m\n"
        f"Min Diff: {np.min(diff):.3f} m\n"
        f"Mean Diff: {np.mean(diff):.3f} m\n"
        f"RMSE (B-A): {np.sqrt(np.mean(diff**2)):.3f} m"
    )
    ax2.text(0.02, 0.98, diff_stats, transform=ax2.transAxes, fontsize=9,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plot_file = (f'{output_dir}/station_{station_idx:04d}_'
                 f'{coops_match["nos_id"]}_overlay_diff.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"+ Saved: {plot_file}")
    print(f"  {label_a}: RMSE={stats_a['rmse']:.3f} m, Corr={stats_a['correlation']:.3f}")
    print(f"  {label_b}: RMSE={stats_b['rmse']:.3f} m, Corr={stats_b['correlation']:.3f}")
    return {
        'plot_file': plot_file,
        'station_idx': station_idx,
        'station_name': info_a['name'],
        'coops_id': coops_match['nos_id'],
        'lon': info_a['lon'],
        'lat': info_a['lat'],
        f'{label_a}_rmse': stats_a['rmse'],
        f'{label_a}_corr': stats_a['correlation'],
        f'{label_b}_rmse': stats_b['rmse'],
        f'{label_b}_corr': stats_b['correlation'],
        'n_points': stats_a['n_points'],
    }


def combine_plots_to_pdf(plots_dir, output_pdf):
    """Combine all PNG plots in plots_dir into a single multi-page PDF."""
    from PIL import Image
    png_files = sorted(f for f in os.listdir(plots_dir) if f.endswith('.png'))
    if not png_files:
        print("No PNG files found to combine")
        return False
    print(f"\nCombining {len(png_files)} plots into PDF...")
    images = []
    for png_file in png_files:
        img = Image.open(os.path.join(plots_dir, png_file))
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f"PDF saved: {output_pdf}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Two fort.61 runs + CO-OPS obs (top panel) with difference panel below')
    parser.add_argument('--file-a', required=True, help='First fort.61.nc file')
    parser.add_argument('--file-b', required=True, help='Second fort.61.nc file')
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--station-idx', type=int, help='Single station index')
    g.add_argument('--station-range', nargs=2, type=int, metavar=('START', 'END'),
                   help='Range of stations to process (END exclusive)')
    parser.add_argument('--label-a', default='Run A')
    parser.add_argument('--label-b', default='Run B')
    parser.add_argument('--datum', default='MSL')
    parser.add_argument('--output-dir', default='comparison_plots')
    parser.add_argument('--output-pdf', default=None,
                        help='Combine output PNGs into a single PDF')
    parser.add_argument('--search-radius', type=float, default=0.01,
                        help='CO-OPS search radius in degrees (default 0.01)')
    args = parser.parse_args()

    if args.station_idx is not None:
        stations = [args.station_idx]
    else:
        stations = list(range(args.station_range[0], args.station_range[1]))

    print("=" * 80)
    print("Two-Model + CO-OPS Comparison with Difference Panel")
    print("=" * 80)
    print(f"File A ({args.label_a}): {args.file_a}")
    print(f"File B ({args.label_b}): {args.file_b}")
    print(f"Datum: {args.datum}")
    print(f"Output: {args.output_dir}/")
    print(f"Stations: {len(stations)}")

    results = []
    for idx in stations:
        try:
            r = create_plot(args.file_a, args.file_b, idx,
                            datum=args.datum, output_dir=args.output_dir,
                            label_a=args.label_a, label_b=args.label_b,
                            search_radius=args.search_radius)
            if r:
                results.append(r)
        except Exception as e:
            print(f"X Error processing station {idx}: {e}")

    if results and len(stations) > 1:
        import statistics
        rmse_a = [r[f'{args.label_a}_rmse'] for r in results]
        rmse_b = [r[f'{args.label_b}_rmse'] for r in results]
        print(f"\n{'=' * 80}\nSUMMARY ({len(results)}/{len(stations)} stations)\n{'=' * 80}")
        print(f"{args.label_a}:  Mean RMSE = {statistics.mean(rmse_a):.4f} m")
        print(f"{args.label_b}:  Mean RMSE = {statistics.mean(rmse_b):.4f} m")

    if args.output_pdf and results:
        combine_plots_to_pdf(args.output_dir, args.output_pdf)

    print(f"\n+ Completed: {len(results)}/{len(stations)} stations")
    print(f"+ Plots saved to: {args.output_dir}/")
