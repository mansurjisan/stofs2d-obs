"""
Model-Observation Comparison
============================

Module for comparing STOFS2D model output with CO-OPS observations,
including statistical analysis and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class ModelObsComparison:
    """Compare STOFS2D model output with CO-OPS observations"""

    def __init__(self, model_data, obs_data, station_name, model_name='STOFS2D', datum='MSL'):
        """
        Initialize comparison

        Parameters:
        -----------
        model_data : pandas.DataFrame
            Model timeseries with 'water_level' column
        obs_data : pandas.DataFrame
            Observation timeseries with 'v' (value) column
        station_name : str
            Station name for labeling
        model_name : str
            Model name for labeling
        datum : str
            Vertical datum for observations (e.g., 'MSL', 'MLLW', 'NAVD88')
        """
        self.model_data = model_data
        self.obs_data = obs_data
        self.station_name = station_name
        self.model_name = model_name
        self.datum = datum

        # Align data to common time index
        self._align_data()

    def _align_data(self):
        """Align model and observation data to common time index"""
        # Check if observation data is empty or invalid
        if len(self.obs_data) == 0:
            print("\nWarning: No observation data available")
            self.aligned = pd.DataFrame(columns=['model', 'obs'])
            return

        # Rename observation column for consistency
        if 'v' in self.obs_data.columns:
            self.obs_data = self.obs_data.rename(columns={'v': 'obs_water_level'})
        elif 'obs_water_level' not in self.obs_data.columns:
            # Try to find a numeric column to use
            numeric_cols = self.obs_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.obs_data = self.obs_data.rename(columns={numeric_cols[0]: 'obs_water_level'})
            else:
                print("\nWarning: No valid observation data columns found")
                self.aligned = pd.DataFrame(columns=['model', 'obs'])
                return

        # Handle timezone mismatch - localize model data to UTC if needed
        model_index = self.model_data.index
        obs_index = self.obs_data.index

        # Check if one is tz-aware and the other isn't
        if model_index.tz is None and obs_index.tz is not None:
            # Localize model data to UTC
            self.model_data.index = self.model_data.index.tz_localize('UTC')
        elif model_index.tz is not None and obs_index.tz is None:
            # Localize obs data to UTC
            self.obs_data.index = self.obs_data.index.tz_localize('UTC')

        # Merge on time index
        self.aligned = pd.merge(
            self.model_data[['water_level']].rename(columns={'water_level': 'model'}),
            self.obs_data[['obs_water_level']].rename(columns={'obs_water_level': 'obs'}),
            left_index=True,
            right_index=True,
            how='inner'
        )

        print(f"\nData alignment:")
        print(f"  Model points: {len(self.model_data)}")
        print(f"  Observation points: {len(self.obs_data)}")
        print(f"  Aligned points: {len(self.aligned)}")

    def calculate_statistics(self):
        """
        Calculate validation statistics

        Returns:
        --------
        dict : Statistical metrics
        """
        if len(self.aligned) == 0:
            print("Warning: No overlapping data for statistics")
            return {}

        model_vals = self.aligned['model'].values
        obs_vals = self.aligned['obs'].values

        # Calculate metrics
        diff = model_vals - obs_vals

        stats = {
            'n_points': len(self.aligned),
            'rmse': np.sqrt(np.mean(diff**2)),
            'mae': np.mean(np.abs(diff)),
            'bias': np.mean(diff),
            'correlation': np.corrcoef(model_vals, obs_vals)[0, 1],
            'model_mean': np.mean(model_vals),
            'model_std': np.std(model_vals),
            'model_max': np.max(model_vals),
            'model_min': np.min(model_vals),
            'obs_mean': np.mean(obs_vals),
            'obs_std': np.std(obs_vals),
            'obs_max': np.max(obs_vals),
            'obs_min': np.min(obs_vals),
        }

        # Calculate skill score (Murphy 1988)
        obs_variance = np.var(obs_vals)
        if obs_variance > 0:
            stats['skill_score'] = 1 - (stats['rmse']**2 / obs_variance)
        else:
            stats['skill_score'] = np.nan

        return stats

    def print_statistics(self):
        """Print validation statistics"""
        stats = self.calculate_statistics()

        if not stats:
            return

        print(f"\n{'='*60}")
        print(f"Validation Statistics: {self.station_name}")
        print(f"{'='*60}")
        print(f"Data points:      {stats['n_points']}")
        print(f"\nError Metrics:")
        print(f"  RMSE:           {stats['rmse']:.4f} m")
        print(f"  MAE:            {stats['mae']:.4f} m")
        print(f"  Bias:           {stats['bias']:+.4f} m")
        print(f"  Correlation:    {stats['correlation']:.4f}")
        print(f"  Skill Score:    {stats['skill_score']:.4f}")
        print(f"\nModel Statistics:")
        print(f"  Mean:           {stats['model_mean']:.4f} m")
        print(f"  Std Dev:        {stats['model_std']:.4f} m")
        print(f"  Range:          [{stats['model_min']:.4f}, {stats['model_max']:.4f}] m")
        print(f"\nObservation Statistics:")
        print(f"  Mean:           {stats['obs_mean']:.4f} m")
        print(f"  Std Dev:        {stats['obs_std']:.4f} m")
        print(f"  Range:          [{stats['obs_min']:.4f}, {stats['obs_max']:.4f}] m")
        print(f"{'='*60}\n")

    def plot_comparison(self, save_path=None):
        """
        Create comprehensive comparison plot

        Parameters:
        -----------
        save_path : str, optional
            Path to save plot
        """
        stats = self.calculate_statistics()

        if len(self.aligned) == 0:
            print("Warning: No data to plot")
            return

        # Create figure with 2 subplots (removed scatter plot)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

        # --- Subplot 1: Timeseries comparison ---
        ax1.plot(self.model_data.index, self.model_data['water_level'],
                'b-', linewidth=1.5, label=f'{self.model_name} Model', alpha=0.8)
        ax1.plot(self.obs_data.index, self.obs_data['obs_water_level'],
                'r-', linewidth=1.5, label='CO-OPS Observation', alpha=0.8)

        ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        ax1.set_ylabel(f'Water Level (m, {self.datum})', fontsize=11)
        ax1.set_title(f'{self.model_name} vs CO-OPS Observations: {self.station_name}',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right', fontsize=10)

        # Add statistics text box (only RMSE)
        if stats:
            stats_text = f'RMSE: {stats["rmse"]:.3f} m'
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round',
                    facecolor='wheat', alpha=0.7))

        # --- Subplot 2: Difference (Model - Obs) ---
        if len(self.aligned) > 0:
            diff = self.aligned['model'] - self.aligned['obs']
            ax2.plot(self.aligned.index, diff, 'k-', linewidth=1.5, alpha=0.8)
            ax2.fill_between(self.aligned.index, diff, 0,
                           where=(diff >= 0), color='red', alpha=0.3, label='Over-prediction')
            ax2.fill_between(self.aligned.index, diff, 0,
                           where=(diff < 0), color='blue', alpha=0.3, label='Under-prediction')

            ax2.axhline(y=0, color='k', linestyle='--', linewidth=1)
            ax2.set_ylabel('Difference (m)', fontsize=11)
            ax2.set_xlabel('Date/Time', fontsize=11)
            ax2.set_title('Model - Observation Difference', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='upper right', fontsize=9)

        # Format x-axis dates
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        else:
            plt.show()

        plt.close()
