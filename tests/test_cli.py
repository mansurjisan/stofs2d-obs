"""
Tests for CLI functions
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from stofs2d_obs.cli import (
    list_stations_command,
    save_statistics,
    generate_summary_csv,
    generate_html_report
)


@pytest.mark.unit
class TestCLIFunctions:
    """Test suite for CLI helper functions"""

    def test_list_stations_command(self, mock_fort61_file, capsys):
        """Test list_stations_command function"""
        result = list_stations_command(mock_fort61_file, n=3)

        assert result == 0  # Success exit code

        captured = capsys.readouterr()
        assert 'Stations in' in captured.out
        assert 'Test Station' in captured.out

    def test_save_statistics_csv(self, temp_dir, mock_station_info, mock_coops_match):
        """Test saving statistics to CSV file"""
        stats = {
            'rmse': 0.123,
            'mae': 0.111,
            'bias': 0.050,
            'correlation': 0.95,
            'n_points': 100
        }

        output_file = Path(temp_dir) / 'stats.csv'

        save_statistics(stats, str(output_file), mock_station_info, mock_coops_match)

        assert output_file.exists()

        # Read and check contents
        content = output_file.read_text()
        assert 'rmse' in content
        assert '0.123' in content
        assert 'Magueyes Island' in content

    def test_save_statistics_json(self, temp_dir, mock_station_info, mock_coops_match):
        """Test saving statistics to JSON file"""
        import json

        stats = {
            'rmse': 0.123,
            'mae': 0.111,
            'bias': 0.050,
            'correlation': 0.95,
            'n_points': 100
        }

        output_file = Path(temp_dir) / 'stats.json'

        save_statistics(stats, str(output_file), mock_station_info, mock_coops_match)

        assert output_file.exists()

        # Read and verify JSON
        with open(output_file, 'r') as f:
            data = json.load(f)

        assert data['rmse'] == 0.123
        assert data['correlation'] == 0.95

    def test_generate_summary_csv(self, temp_dir):
        """Test generating batch summary CSV"""
        results = [
            {
                'station_idx': 0,
                'status': 'success',
                'station_name': 'Test Station 1',
                'rmse': 0.15,
                'correlation': 0.90
            },
            {
                'station_idx': 1,
                'status': 'no_coops_match',
                'station_name': 'Test Station 2',
                'error': 'No match found'
            }
        ]

        output_file = Path(temp_dir) / 'summary.csv'

        generate_summary_csv(results, str(output_file))

        assert output_file.exists()

        # Check contents
        content = output_file.read_text()
        assert 'station_idx' in content
        assert 'status' in content
        assert 'Test Station 1' in content
        assert 'success' in content
        assert 'no_coops_match' in content

    def test_generate_html_report(self, temp_dir):
        """Test generating HTML validation report"""
        results = [
            {
                'station_idx': 0,
                'status': 'success',
                'station_name': 'Test Station 1',
                'coops_station': 'CO-OPS Station 1',
                'rmse': 0.15,
                'mae': 0.12,
                'bias': 0.03,
                'correlation': 0.90,
                'n_points': 100
            },
            {
                'station_idx': 1,
                'status': 'no_coops_match',
                'station_name': 'Test Station 2',
                'error': 'No match found'
            },
            {
                'station_idx': 2,
                'status': 'success',
                'station_name': 'Test Station 3',
                'coops_station': 'CO-OPS Station 3',
                'rmse': 0.20,
                'mae': 0.18,
                'bias': 0.05,
                'correlation': 0.85,
                'n_points': 95
            }
        ]

        output_file = Path(temp_dir) / 'report.html'

        generate_html_report(results, str(output_file), 'test_fort.61.nc')

        assert output_file.exists()

        # Check HTML content
        content = output_file.read_text()
        assert '<!DOCTYPE html>' in content
        assert 'STOFS2D Validation Report' in content
        assert 'Test Station 1' in content
        assert 'Success' in content or 'success' in content
        assert '0.15' in content or '0.1500' in content  # RMSE value

    def test_html_report_summary_stats(self, temp_dir):
        """Test that HTML report includes aggregate statistics"""
        results = [
            {
                'station_idx': 0,
                'status': 'success',
                'rmse': 0.10,
                'mae': 0.08,
                'bias': 0.02,
                'correlation': 0.95,
                'station_name': 'Station 1',
                'coops_station': 'COOPS 1',
                'n_points': 100
            },
            {
                'station_idx': 1,
                'status': 'success',
                'rmse': 0.20,
                'mae': 0.18,
                'bias': 0.05,
                'correlation': 0.85,
                'station_name': 'Station 2',
                'coops_station': 'COOPS 2',
                'n_points': 95
            }
        ]

        output_file = Path(temp_dir) / 'report_stats.html'

        generate_html_report(results, str(output_file), 'test.nc')

        content = output_file.read_text()

        # Should show aggregate statistics (averages)
        # Average RMSE should be around 0.15
        assert 'RMSE' in content
        assert 'Correlation' in content

    def test_html_report_handles_failures(self, temp_dir):
        """Test HTML report with only failed stations"""
        results = [
            {
                'station_idx': 0,
                'status': 'no_coops_match',
                'station_name': 'Failed Station 1',
                'error': 'No CO-OPS station within search radius'
            },
            {
                'station_idx': 1,
                'status': 'error',
                'station_name': 'Failed Station 2',
                'error': 'Processing error'
            }
        ]

        output_file = Path(temp_dir) / 'report_failures.html'

        generate_html_report(results, str(output_file), 'test.nc')

        assert output_file.exists()

        content = output_file.read_text()
        assert 'Failed Station 1' in content
        assert 'No CO-OPS station within search radius' in content


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI"""

    def test_list_stations_integration(self, mock_fort61_file):
        """Integration test for listing stations"""
        from stofs2d_obs.cli import main
        import sys

        # Mock command line arguments
        test_args = ['stofs2d-compare', mock_fort61_file, '--list-stations']

        with patch.object(sys, 'argv', test_args):
            result = main()

        assert result == 0

    def test_help_command(self):
        """Test that --help works"""
        from stofs2d_obs.cli import main
        import sys

        test_args = ['stofs2d-compare', '--help']

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # --help should exit with code 0
            assert exc_info.value.code == 0

    def test_version_command(self):
        """Test that --version works"""
        from stofs2d_obs.cli import main
        import sys

        test_args = ['stofs2d-compare', '--version']

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_file_not_found_error(self):
        """Test CLI handling of non-existent file"""
        from stofs2d_obs.cli import main
        import sys

        test_args = ['stofs2d-compare', 'nonexistent.nc', '--list-stations']

        with patch.object(sys, 'argv', test_args):
            result = main()

        # Should return error code
        assert result == 1
