import pytest
from tests.conftest import *  # noqa: F401,F403 — загружает sys.path и моки

from utils import get_statistics


class TestGetStatistics:
    def test_empty_list(self):
        result = get_statistics([])
        assert result == {"total": 0, "max": 0, "min": 0, "mean": 0, "std": 0}

    def test_single_element(self):
        result = get_statistics([42.0])
        assert result["total"] == 42.0
        assert result["max"] == 42.0
        assert result["min"] == 42.0
        assert result["mean"] == 42.0
        assert result["std"] == 0

    def test_multiple_elements(self):
        result = get_statistics([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result["total"] == 15.0
        assert result["max"] == 5.0
        assert result["min"] == 1.0
        assert abs(result["mean"] - 3.0) < 1e-9
        assert result["std"] > 0

    def test_identical_elements(self):
        result = get_statistics([7.0, 7.0, 7.0])
        assert result["std"] == 0.0
        assert result["mean"] == 7.0

    def test_negative_values(self):
        result = get_statistics([-3.0, -1.0, 1.0, 3.0])
        assert result["min"] == -3.0
        assert result["max"] == 3.0
        assert abs(result["mean"] - 0.0) < 1e-9
