"""
Tests for ModelObsComparison class
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from stofs2d_obs import ModelObsComparison


@pytest.mark.unit
class TestModelObsComparison:
    """Test suite for ModelObsComparison class"""

    def test_init_with_valid_data(self, mock_model_data, mock_obs_data):
        """Test initialization with valid model and observation data"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            model_name='STOFS2D',
            datum='MSL'
        )

        assert comparison.station_name == 'Test Station'
        assert comparison.model_name == 'STOFS2D'
        assert comparison.datum == 'MSL'
        assert comparison.aligned is not None

    def test_data_alignment(self, mock_model_data, mock_obs_data):
        """Test that model and observation data are aligned"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        assert 'model' in comparison.aligned.columns
        assert 'obs' in comparison.aligned.columns
        assert len(comparison.aligned) > 0
        # Should have aligned timestamps
        assert len(comparison.aligned) <= min(len(mock_model_data), len(mock_obs_data))

    def test_calculate_statistics(self, mock_model_data, mock_obs_data):
        """Test calculation of validation statistics"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        stats = comparison.calculate_statistics()

        # Check all expected statistics are present
        assert 'rmse' in stats
        assert 'mae' in stats
        assert 'bias' in stats
        assert 'correlation' in stats
        assert 'skill_score' in stats
        assert 'n_points' in stats
        assert 'model_mean' in stats
        assert 'model_std' in stats
        assert 'obs_mean' in stats
        assert 'obs_std' in stats

    def test_statistics_values(self, mock_model_data, mock_obs_data):
        """Test that statistics have reasonable values"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        stats = comparison.calculate_statistics()

        # RMSE should be non-negative
        assert stats['rmse'] >= 0

        # MAE should be non-negative
        assert stats['mae'] >= 0

        # Correlation should be between -1 and 1
        assert -1 <= stats['correlation'] <= 1

        # Number of points should be positive
        assert stats['n_points'] > 0

        # Standard deviations should be non-negative
        assert stats['model_std'] >= 0
        assert stats['obs_std'] >= 0

    def test_print_statistics(self, mock_model_data, mock_obs_data, capsys):
        """Test printing statistics"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        comparison.print_statistics()

        captured = capsys.readouterr()
        assert 'RMSE' in captured.out
        assert 'MAE' in captured.out
        assert 'Bias' in captured.out
        assert 'Correlation' in captured.out
        assert 'Test Station' in captured.out

    def test_plot_comparison(self, mock_model_data, mock_obs_data, temp_dir):
        """Test generating comparison plot"""
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        output_file = Path(temp_dir) / 'test_plot.png'
        comparison.plot_comparison(save_path=str(output_file))

        # Check file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_empty_observation_data(self, mock_model_data):
        """Test handling of empty observation data"""
        empty_obs = pd.DataFrame({
            'water_level': []
        }, index=pd.DatetimeIndex([]))

        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=empty_obs,
            station_name='Test Station',
            datum='MSL'
        )

        # Should handle empty data gracefully
        assert len(comparison.aligned) == 0

    def test_timezone_handling(self, mock_model_data, mock_obs_data):
        """Test handling of timezone-aware and timezone-naive data"""
        # Model data is tz-naive, obs data is tz-aware
        comparison = ModelObsComparison(
            model_data=mock_model_data,
            obs_data=mock_obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        # Should handle timezone differences
        assert comparison.aligned is not None
        assert len(comparison.aligned) > 0

    def test_partial_overlap(self):
        """Test handling of partial time overlap"""
        # Set random seed for reproducibility
        np.random.seed(42)

        # Model data: 100 hours starting Jan 1
        model_data = pd.DataFrame({
            'water_level': np.random.randn(100)
        }, index=pd.date_range('2025-01-01', periods=100, freq='H'))

        # Obs data: 50 hours starting Jan 2
        obs_data = pd.DataFrame({
            'water_level': np.random.randn(50)
        }, index=pd.date_range('2025-01-02', periods=50, freq='H', tz='UTC'))

        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        # Should only align overlapping period
        assert 0 < len(comparison.aligned) < 100

    def test_no_overlap(self):
        """Test handling of no time overlap"""
        # Set random seed for reproducibility
        np.random.seed(42)

        # Model data: Jan 1-5
        model_data = pd.DataFrame({
            'water_level': np.random.randn(100)
        }, index=pd.date_range('2025-01-01', periods=100, freq='H'))

        # Obs data: Feb 1-5 (no overlap)
        obs_data = pd.DataFrame({
            'water_level': np.random.randn(100)
        }, index=pd.date_range('2025-02-01', periods=100, freq='H', tz='UTC'))

        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        # Should have no aligned data
        assert len(comparison.aligned) == 0

    def test_perfect_correlation(self):
        """Test statistics with perfect correlation"""
        # Set random seed for reproducibility
        np.random.seed(42)

        # Create identical data
        time_index = pd.date_range('2025-01-01', periods=100, freq='H')
        data_values = np.random.randn(100)

        model_data = pd.DataFrame({
            'water_level': data_values
        }, index=time_index)

        obs_data = pd.DataFrame({
            'water_level': data_values
        }, index=time_index.tz_localize('UTC'))

        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        stats = comparison.calculate_statistics()

        # Should have perfect correlation
        assert abs(stats['correlation'] - 1.0) < 0.01
        # RMSE should be near zero
        assert stats['rmse'] < 0.01
        # Bias should be near zero
        assert abs(stats['bias']) < 0.01

    def test_bias_calculation(self):
        """Test bias calculation"""
        # Set random seed for reproducibility
        np.random.seed(42)

        time_index = pd.date_range('2025-01-01', periods=100, freq='H')

        # Model data with constant offset of +0.5
        model_data = pd.DataFrame({
            'water_level': np.random.randn(100) + 1.0
        }, index=time_index)

        obs_data = pd.DataFrame({
            'water_level': np.random.randn(100) + 0.5
        }, index=time_index.tz_localize('UTC'))

        comparison = ModelObsComparison(
            model_data=model_data,
            obs_data=obs_data,
            station_name='Test Station',
            datum='MSL'
        )

        stats = comparison.calculate_statistics()

        # Bias should be approximately +0.5
        assert 0.3 < stats['bias'] < 0.7
