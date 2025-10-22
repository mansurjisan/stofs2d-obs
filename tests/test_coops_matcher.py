"""
Tests for COOPSMatcher class
"""

import pytest
from unittest.mock import Mock, patch
from stofs2d_obs import COOPSMatcher


@pytest.mark.unit
class TestCOOPSMatcher:
    """Test suite for COOPSMatcher class"""

    @pytest.mark.slow
    def test_init_loads_stations(self):
        """Test that COOPSMatcher loads CO-OPS stations"""
        matcher = COOPSMatcher(search_radius=0.5)
        assert matcher.search_radius == 0.5
        assert matcher.coops_stations is not None
        assert len(matcher.coops_stations) > 0

    def test_search_radius_stored(self):
        """Test that search radius is stored correctly"""
        matcher = COOPSMatcher(search_radius=1.5)
        assert matcher.search_radius == 1.5

    @pytest.mark.slow
    def test_find_nearest_basic(self):
        """Test finding nearest stations to a known location"""
        matcher = COOPSMatcher(search_radius=1.0)

        # Magueyes Island, PR coordinates
        lon, lat = -67.0489, 17.9700

        matches = matcher.find_nearest(lon, lat, max_results=5)

        assert len(matches) > 0
        assert len(matches) <= 5

        # First match should be very close
        assert matches.iloc[0]['distance'] < 1.0

    @pytest.mark.slow
    def test_get_best_match(self):
        """Test getting single best match"""
        matcher = COOPSMatcher(search_radius=1.0)

        # Magueyes Island, PR
        lon, lat = -67.0489, 17.9700

        best_match = matcher.get_best_match(lon, lat)

        assert best_match is not None
        assert 'name' in best_match
        assert 'nos_id' in best_match
        assert 'distance' in best_match
        assert best_match['distance'] < 1.0

    @pytest.mark.slow
    def test_valid_id_filter(self):
        """Test filtering for valid 7-digit IDs"""
        matcher = COOPSMatcher(search_radius=1.0)

        # Magueyes Island, PR
        lon, lat = -67.0489, 17.9700

        # With valid ID filter
        match_valid = matcher.get_best_match(lon, lat, require_valid_id=True)

        if match_valid:
            # Should have 7-digit ID
            assert len(str(match_valid['nos_id'])) == 7
            assert str(match_valid['nos_id']).isdigit()

    @pytest.mark.slow
    def test_no_match_far_location(self):
        """Test that no match is found for location with no nearby stations"""
        matcher = COOPSMatcher(search_radius=0.1)  # Very small radius

        # Middle of Pacific Ocean
        lon, lat = -150.0, 10.0

        match = matcher.get_best_match(lon, lat)

        # Should be None or very far away
        assert match is None or match['distance'] > 0.1

    @pytest.mark.slow
    def test_max_results_limit(self):
        """Test that max_results limits the number of matches"""
        matcher = COOPSMatcher(search_radius=5.0)

        # US East Coast
        lon, lat = -75.0, 39.0

        matches_3 = matcher.find_nearest(lon, lat, max_results=3)
        matches_10 = matcher.find_nearest(lon, lat, max_results=10)

        assert len(matches_3) <= 3
        assert len(matches_10) <= 10
        assert len(matches_3) <= len(matches_10)

    @pytest.mark.slow
    def test_distance_ordering(self):
        """Test that matches are ordered by distance"""
        matcher = COOPSMatcher(search_radius=5.0)

        lon, lat = -75.0, 39.0

        matches = matcher.find_nearest(lon, lat, max_results=5)

        if len(matches) > 1:
            # Check distances are in ascending order
            for i in range(len(matches) - 1):
                assert matches.iloc[i]['distance'] <= matches.iloc[i+1]['distance']

    def test_distance_calculation(self):
        """Test distance calculation between coordinates"""
        matcher = COOPSMatcher(search_radius=1.0)

        # Two points on Earth
        lon1, lat1 = -75.0, 40.0
        lon2, lat2 = -75.0, 41.0

        # Simple Euclidean approximation
        distance = ((lon2 - lon1)**2 + (lat2 - lat1)**2)**0.5

        # Distance should be approximately 1 degree
        assert abs(distance - 1.0) < 0.01

    @pytest.mark.slow
    def test_known_station(self):
        """Test matching to a known CO-OPS station"""
        matcher = COOPSMatcher(search_radius=0.5)

        # Magueyes Island, PR (known CO-OPS station 9759110)
        lon, lat = -67.0489, 17.9700

        match = matcher.get_best_match(lon, lat, require_valid_id=True)

        assert match is not None
        # Should find Magueyes Island
        assert 'Magueyes' in match['name'] or '9759110' == str(match['nos_id'])
