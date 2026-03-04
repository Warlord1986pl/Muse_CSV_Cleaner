from muse_csv_cleaner.cli import _to_snake_case


def test_cells_per_ul_normalization():
    assert _to_snake_case("Cells/µL") == "cells_per_ul"


def test_percent_positive_normalization():
    result = _to_snake_case("% ROS(+) Cells (M2)")
    assert result == "percent_ros_positive_cells_m2"
