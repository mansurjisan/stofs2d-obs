"""
Command-Line Interface for STOFS2D-OBS
======================================

CLI for comparing STOFS2D model output with CO-OPS observations.
"""

import argparse
import os
import sys
from pathlib import Path

from searvey import fetch_coops_station

from stofs2d_obs import COOPSMatcher, Fort61Reader, ModelObsComparison


def list_stations_command(nc_file, n=20):
    """List available stations in the fort.61.nc file"""
    print(f"\n{'='*70}")
    print(f"Stations in {nc_file}")
    print(f"{'='*70}\n")

    with Fort61Reader(nc_file) as fort61:
        fort61.list_stations(n=n)

    print(f"\n{'='*70}")
    return 0


def compare_station(
    nc_file,
    station_idx,
    datum="MSL",
    search_radius=0.5,
    plot_file=None,
    stats_file=None,
    verbose=False,
    quiet=False,
):
    """
    Compare a single station with CO-OPS observations

    Parameters:
        nc_file: Path to fort.61.nc file
        station_idx: Station index to process
        datum: Vertical datum (MSL, MLLW, NAVD88, STND)
        search_radius: CO-OPS search radius in degrees
        plot_file: Path to save comparison plot
        stats_file: Path to save statistics (CSV)
        verbose: Verbose output
        quiet: Minimal output
    """
    if not quiet:
        print(f"\n{'='*70}")
        print("STOFS2D-OBS: Model-Observation Comparison")
        print(f"{'='*70}\n")

    try:
        # Step 1: Read STOFS2D model data
        if verbose:
            print(f"[1/5] Opening {nc_file}...")

        with Fort61Reader(nc_file) as fort61:
            # Get station information
            if verbose:
                print(f"[2/5] Reading station {station_idx}...")

            station_info = fort61.get_station_info(station_idx)

            if not quiet:
                print(f"Station: {station_info['name']}")
                print(f"Location: ({station_info['lon']:.4f}, {station_info['lat']:.4f})")
                time_start = station_info["time_range"][0]
                time_end = station_info["time_range"][1]
                print(f"Time range: {time_start} to {time_end}")

            # Extract model timeseries
            model_data = fort61.get_station_data(station_idx)

            if verbose:
                print(f"Model data points: {len(model_data)}")

            # Step 2: Find matching CO-OPS station
            if verbose:
                print(f"\n[3/5] Finding nearest CO-OPS station (radius={search_radius}°)...")

            matcher = COOPSMatcher(search_radius=search_radius)
            coops_match = matcher.get_best_match(
                station_info["lon"], station_info["lat"], require_valid_id=True
            )

            if coops_match is None:
                print(
                    f"\nERROR: No CO-OPS station found within {search_radius}° of station location"
                )
                print("Try increasing --search-radius")
                return 1

            if not quiet:
                print(f"\nCO-OPS Station: {coops_match['name']} (ID: {coops_match['nos_id']})")
                dist_deg = coops_match["distance"]
                dist_km = dist_deg * 111
                print(f"Distance: {dist_deg:.4f}° (~{dist_km:.1f} km)")

            # Step 3: Fetch CO-OPS observation data
            if verbose:
                print(f"\n[4/5] Fetching CO-OPS data (datum={datum})...")

            try:
                obs_data = fetch_coops_station(
                    station_id=coops_match["nos_id"],
                    start_date=station_info["time_range"][0],
                    end_date=station_info["time_range"][1],
                    product="water_level",
                    datum=datum,
                )
            except Exception as e:
                print(f"\nERROR fetching CO-OPS data: {e}")
                if verbose:
                    print("\nTrying alternate datums...")

                # Try alternate datums
                for alt_datum in ["MSL", "MLLW", "STND", "NAVD88"]:
                    if alt_datum == datum:
                        continue
                    try:
                        if verbose:
                            print(f"  Trying {alt_datum}...")
                        obs_data = fetch_coops_station(
                            station_id=coops_match["nos_id"],
                            start_date=station_info["time_range"][0],
                            end_date=station_info["time_range"][1],
                            product="water_level",
                            datum=alt_datum,
                        )
                        datum = alt_datum
                        if verbose:
                            print(f"  Success with {alt_datum}!")
                        break
                    except Exception:
                        continue
                else:
                    print("\nERROR: Could not fetch observation data with any datum")
                    return 1

            if len(obs_data) == 0:
                print("\nERROR: No observation data available for this time period")
                return 1

            if verbose:
                print(f"Observation data points: {len(obs_data)}")

            # Step 4: Create comparison
            if verbose:
                print("\n[5/5] Creating comparison and calculating statistics...")

            comparison = ModelObsComparison(
                model_data=model_data,
                obs_data=obs_data,
                station_name=f"{station_info['name']} / {coops_match['name']}",
                model_name="STOFS2D",
                datum=datum,
            )

            # Calculate and display statistics
            stats = comparison.calculate_statistics()

            if not quiet:
                print(f"\n{'='*70}")
                comparison.print_statistics()
                print(f"{'='*70}")

            # Save statistics to file if requested
            if stats_file:
                save_statistics(stats, stats_file, station_info, coops_match)
                if not quiet:
                    print(f"\nStatistics saved to: {stats_file}")

            # Generate plot if requested
            if plot_file:
                if verbose:
                    print(f"\nGenerating plot: {plot_file}")
                comparison.plot_comparison(save_path=plot_file)
                if not quiet:
                    print(f"Plot saved to: {plot_file}")

        if not quiet:
            print(f"\n{'='*70}")
            print("Comparison complete!")
            print(f"{'='*70}\n")

        return 0

    except FileNotFoundError:
        print(f"\nERROR: File not found: {nc_file}")
        return 1
    except IndexError:
        print(f"\nERROR: Station index {station_idx} not found in file")
        print("Use --list-stations to see available stations")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


def save_statistics(stats, output_file, station_info, coops_match):
    """Save statistics to CSV or JSON file"""
    import json

    output_path = Path(output_file)

    # Combine all info
    full_stats = {
        "station_name": station_info["name"],
        "station_lon": station_info["lon"],
        "station_lat": station_info["lat"],
        "coops_station": coops_match["name"],
        "coops_id": coops_match["nos_id"],
        "coops_distance_deg": coops_match["distance"],
        "coops_distance_km": coops_match["distance"] * 111,
        **stats,
    }

    if output_path.suffix.lower() == ".json":
        with open(output_file, "w") as f:
            json.dump(full_stats, f, indent=2, default=str)
    else:
        # CSV format
        import csv

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in full_stats.items():
                writer.writerow([key, value])


def batch_process_stations(
    nc_file, station_indices=None, datum="MSL", search_radius=0.5, save_plots=None, verbose=False
):
    """
    Process multiple stations and return results

    Parameters:
        nc_file: Path to fort.61.nc file
        station_indices: List of station indices to process (None = all)
        datum: Vertical datum
        search_radius: CO-OPS search radius
        save_plots: Directory to save plots (None = don't save)
        verbose: Verbose output

    Returns:
        List of result dictionaries
    """
    results = []

    with Fort61Reader(nc_file) as fort61:
        # Determine which stations to process
        if station_indices is None:
            # Get total number of stations
            import netCDF4 as nc

            ds = nc.Dataset(nc_file, "r")
            n_stations = len(ds.variables["station_name"])
            ds.close()
            station_indices = range(n_stations)

        # Initialize CO-OPS matcher once
        matcher = COOPSMatcher(search_radius=search_radius)

        # Process each station
        from tqdm import tqdm

        for idx in tqdm(station_indices, desc="Processing stations", disable=verbose):
            try:
                # Get station info
                station_info = fort61.get_station_info(idx)
                model_data = fort61.get_station_data(idx)

                # Find CO-OPS match
                coops_match = matcher.get_best_match(
                    station_info["lon"], station_info["lat"], require_valid_id=True
                )

                if coops_match is None:
                    if verbose:
                        print(f"Station {idx}: No CO-OPS match found")
                    results.append(
                        {
                            "station_idx": idx,
                            "station_name": station_info["name"],
                            "status": "no_coops_match",
                            "error": "No CO-OPS station within search radius",
                        }
                    )
                    continue

                # Try to fetch observations
                obs_data = None
                used_datum = datum

                for try_datum in [datum, "MSL", "MLLW", "STND", "NAVD88"]:
                    if obs_data is not None:
                        break
                    try:
                        obs_data = fetch_coops_station(
                            station_id=coops_match["nos_id"],
                            start_date=station_info["time_range"][0],
                            end_date=station_info["time_range"][1],
                            product="water_level",
                            datum=try_datum,
                        )
                        if len(obs_data) > 0:
                            used_datum = try_datum
                            break
                    except Exception:
                        continue

                if obs_data is None or len(obs_data) == 0:
                    if verbose:
                        print(f"Station {idx}: No observation data available")
                    results.append(
                        {
                            "station_idx": idx,
                            "station_name": station_info["name"],
                            "coops_station": coops_match["name"],
                            "coops_id": coops_match["nos_id"],
                            "status": "no_obs_data",
                            "error": "No observation data available",
                        }
                    )
                    continue

                # Create comparison
                comparison = ModelObsComparison(
                    model_data=model_data,
                    obs_data=obs_data,
                    station_name=f"{station_info['name']} / {coops_match['name']}",
                    model_name="STOFS2D",
                    datum=used_datum,
                )

                stats = comparison.calculate_statistics()

                # Save plot if requested
                plot_path = None
                if save_plots:
                    plot_dir = Path(save_plots)
                    plot_dir.mkdir(parents=True, exist_ok=True)
                    plot_path = plot_dir / f"station_{idx:04d}.png"
                    comparison.plot_comparison(save_path=str(plot_path))

                # Store results
                results.append(
                    {
                        "station_idx": idx,
                        "station_name": station_info["name"],
                        "station_lon": station_info["lon"],
                        "station_lat": station_info["lat"],
                        "coops_station": coops_match["name"],
                        "coops_id": coops_match["nos_id"],
                        "coops_distance_deg": coops_match["distance"],
                        "coops_distance_km": coops_match["distance"] * 111,
                        "datum": used_datum,
                        "status": "success",
                        "plot_path": str(plot_path) if plot_path else None,
                        **stats,
                    }
                )

                if verbose:
                    print(f"Station {idx}: Success (RMSE={stats['rmse']:.3f}m)")

            except Exception as e:
                if verbose:
                    print(f"Station {idx}: Error - {e}")
                results.append({"station_idx": idx, "status": "error", "error": str(e)})

    return results


def generate_summary_csv(results, output_file):
    """Generate CSV summary of batch results"""
    import csv

    with open(output_file, "w", newline="") as f:
        # Determine all possible fields
        all_fields = set()
        for result in results:
            all_fields.update(result.keys())

        fieldnames = [
            "station_idx",
            "status",
            "station_name",
            "coops_station",
            "coops_id",
            "rmse",
            "mae",
            "bias",
            "correlation",
            "n_points",
            "datum",
            "coops_distance_km",
            "error",
        ]

        # Add any additional fields
        for field in sorted(all_fields):
            if field not in fieldnames:
                fieldnames.append(field)

        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for result in results:
            writer.writerow(result)


def generate_html_report(results, output_file, nc_file):
    """Generate HTML validation report"""
    from datetime import datetime

    # Calculate summary statistics
    total = len(results)
    successful = sum(1 for r in results if r.get("status") == "success")
    no_match = sum(1 for r in results if r.get("status") == "no_coops_match")
    no_data = sum(1 for r in results if r.get("status") == "no_obs_data")
    errors = sum(1 for r in results if r.get("status") == "error")

    success_results = [r for r in results if r.get("status") == "success"]

    # Calculate aggregate statistics
    if success_results:
        avg_rmse = sum(r["rmse"] for r in success_results) / len(success_results)
        avg_mae = sum(r["mae"] for r in success_results) / len(success_results)
        avg_bias = sum(r["bias"] for r in success_results) / len(success_results)
        avg_corr = sum(r["correlation"] for r in success_results) / len(success_results)
    else:
        avg_rmse = avg_mae = avg_bias = avg_corr = 0

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>STOFS2D Validation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .summary-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .summary-card h3 {{
            margin: 0;
            font-size: 36px;
            font-weight: bold;
        }}
        .summary-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-error {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .status-warning {{
            color: #f39c12;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}
        .stats-table {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .stats-table table {{
            margin: 0;
        }}
        .stats-table th {{
            background-color: #34495e;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>STOFS2D Validation Report</h1>

        <p><strong>Input File:</strong> {nc_file}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>{total}</h3>
                <p>Total Stations</p>
            </div>
            <div class="summary-card success">
                <h3>{successful}</h3>
                <p>Successful ({successful/total*100:.1f}%)</p>
            </div>
            <div class="summary-card warning">
                <h3>{no_match + no_data + errors}</h3>
                <p>Failed ({(no_match + no_data + errors)/total*100:.1f}%)</p>
            </div>
        </div>

        <div class="stats-table">
            <h3>Aggregate Statistics (Successful Stations)</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Mean Value</th>
                </tr>
                <tr>
                    <td>RMSE</td>
                    <td>{avg_rmse:.4f} m</td>
                </tr>
                <tr>
                    <td>MAE</td>
                    <td>{avg_mae:.4f} m</td>
                </tr>
                <tr>
                    <td>Bias</td>
                    <td>{avg_bias:+.4f} m</td>
                </tr>
                <tr>
                    <td>Correlation</td>
                    <td>{avg_corr:.4f}</td>
                </tr>
            </table>
        </div>

        <h2>Station Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Index</th>
                    <th>Station Name</th>
                    <th>CO-OPS Station</th>
                    <th>RMSE (m)</th>
                    <th>Correlation</th>
                    <th>Data Points</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

    for result in results:
        status = result.get("status", "unknown")
        idx = result.get("station_idx", "?")
        station_name = result.get("station_name", "Unknown")
        coops_station = result.get("coops_station", "-")

        if status == "success":
            rmse = f"{result['rmse']:.4f}"
            corr = f"{result['correlation']:.4f}"
            n_points = result.get("n_points", "-")
            status_class = "status-success"
            status_text = "Success"
        else:
            rmse = "-"
            corr = "-"
            n_points = "-"
            status_class = "status-error" if status == "error" else "status-warning"
            error = result.get("error", status)
            status_text = error

        html += f"""                <tr>
                    <td>{idx}</td>
                    <td>{station_name}</td>
                    <td>{coops_station}</td>
                    <td>{rmse}</td>
                    <td>{corr}</td>
                    <td>{n_points}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
"""

    html += """            </tbody>
        </table>

        <div class="footer">
            <p>Generated by STOFS2D-OBS v0.1.0</p>
            <p>https://github.com/oceanmodeling/stofs2d-obs</p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, "w") as f:
        f.write(html)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="stofs2d-compare",
        description="Compare STOFS2D model output with CO-OPS tide gauge observations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available stations (first 20 by default)
  stofs2d-compare fort.61.nc --list-stations

  # List first 40 stations
  stofs2d-compare fort.61.nc --list-stations --max-list 40

  # List all stations
  stofs2d-compare fort.61.nc --list-stations --max-list 0

  # Compare single station and generate plot
  stofs2d-compare fort.61.nc --station-idx 30 --plot comparison.png

  # BATCH PROCESSING: Process first 50 stations
  stofs2d-compare fort.61.nc --batch --max-stations 50 --summary-csv results.csv

  # BATCH PROCESSING: Process station range with HTML report
  stofs2d-compare fort.61.nc --station-range 0 100 --html-report report.html

  # BATCH PROCESSING: Full validation with plots
  stofs2d-compare fort.61.nc --batch --summary-csv results.csv \\
      --html-report report.html --save-plots plots/

For more information, see: https://github.com/oceanmodeling/stofs2d-obs
        """,
    )

    # Required arguments
    parser.add_argument("nc_file", help="Path to fort.61.nc file")

    # Station selection
    station_group = parser.add_mutually_exclusive_group()
    station_group.add_argument(
        "--station-idx", type=int, metavar="N", help="Station index to process (0-based)"
    )
    station_group.add_argument(
        "--list-stations", action="store_true", help="List available stations and exit"
    )

    # List stations options
    parser.add_argument(
        "--max-list",
        type=int,
        metavar="N",
        default=20,
        help="Maximum number of stations to list (default: 20, use 0 for all)",
    )
    station_group.add_argument(
        "--batch", action="store_true", help="Batch process multiple stations"
    )
    station_group.add_argument(
        "--station-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Process station range (inclusive)",
    )

    # Batch processing options
    parser.add_argument(
        "--max-stations",
        type=int,
        metavar="N",
        help="Maximum number of stations to process (with --batch)",
    )
    parser.add_argument(
        "--summary-csv", type=str, metavar="FILE", help="Save batch summary to CSV file"
    )
    parser.add_argument(
        "--html-report", type=str, metavar="FILE", help="Generate HTML validation report"
    )
    parser.add_argument(
        "--save-plots",
        type=str,
        metavar="DIR",
        help="Save plots to directory (batch processing only)",
    )

    # Output options
    parser.add_argument(
        "--plot", type=str, metavar="FILE", help="Save comparison plot to file (PNG, PDF, SVG)"
    )
    parser.add_argument(
        "--stats-file", type=str, metavar="FILE", help="Save statistics to file (CSV or JSON)"
    )

    # CO-OPS options
    parser.add_argument(
        "--datum",
        type=str,
        default="MSL",
        choices=["MSL", "MLLW", "NAVD88", "STND"],
        help="Vertical datum for observations (default: MSL)",
    )
    parser.add_argument(
        "--search-radius",
        type=float,
        default=0.5,
        metavar="RADIUS",
        help="CO-OPS station search radius in degrees (default: 0.5)",
    )

    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output (only errors)")
    parser.add_argument("--version", action="version", version="stofs2d-obs 0.1.0")

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.nc_file):
        print(f"ERROR: File not found: {args.nc_file}")
        return 1

    # Execute appropriate command
    if args.list_stations:
        return list_stations_command(args.nc_file, n=args.max_list)

    elif args.station_idx is not None:
        return compare_station(
            nc_file=args.nc_file,
            station_idx=args.station_idx,
            datum=args.datum,
            search_radius=args.search_radius,
            plot_file=args.plot,
            stats_file=args.stats_file,
            verbose=args.verbose,
            quiet=args.quiet,
        )

    elif args.batch or args.station_range:
        # Batch processing mode
        if not args.quiet:
            print(f"\n{'='*70}")
            print("STOFS2D-OBS: Batch Processing Mode")
            print(f"{'='*70}\n")

        # Determine station indices to process
        if args.station_range:
            start, end = args.station_range
            station_indices = list(range(start, end + 1))
            if not args.quiet:
                print(f"Processing stations {start} to {end} ({len(station_indices)} stations)")
        else:
            # Get total number of stations
            import netCDF4 as nc

            ds = nc.Dataset(args.nc_file, "r")
            n_stations = len(ds.variables["station_name"])
            ds.close()

            if args.max_stations:
                station_indices = list(range(min(args.max_stations, n_stations)))
                if not args.quiet:
                    print(f"Processing first {len(station_indices)} of {n_stations} stations")
            else:
                station_indices = list(range(n_stations))
                if not args.quiet:
                    print(f"Processing all {n_stations} stations")

        # Run batch processing
        results = batch_process_stations(
            nc_file=args.nc_file,
            station_indices=station_indices,
            datum=args.datum,
            search_radius=args.search_radius,
            save_plots=args.save_plots,
            verbose=args.verbose,
        )

        # Print summary
        if not args.quiet:
            successful = sum(1 for r in results if r.get("status") == "success")
            print(f"\n{'='*70}")
            print("Batch Processing Complete")
            print(f"{'='*70}")
            print(f"Total processed: {len(results)}")
            print(f"Successful: {successful} ({successful/len(results)*100:.1f}%)")
            print(f"Failed: {len(results) - successful}")
            print(f"{'='*70}\n")

        # Generate summary CSV
        if args.summary_csv:
            generate_summary_csv(results, args.summary_csv)
            if not args.quiet:
                print(f"Summary CSV saved to: {args.summary_csv}")

        # Generate HTML report
        if args.html_report:
            generate_html_report(results, args.html_report, args.nc_file)
            if not args.quiet:
                print(f"HTML report saved to: {args.html_report}")

        if not args.quiet:
            print()

        return 0

    else:
        parser.print_help()
        print("\nERROR: Must specify --station-idx, --list-stations, --batch, or --station-range")
        return 1


if __name__ == "__main__":
    sys.exit(main())
