import pytest
from app.services.split.equal_split_service import EqualSplitService

def test_equal_split_calculation_exact():
    # 90 minutes = 5400 seconds into 6 parts -> 900 seconds each
    segments = EqualSplitService.calculate_splits(duration=5400.0, parts=6)
    assert len(segments) == 6
    
    expected_starts = [0.0, 900.0, 1800.0, 2700.0, 3600.0, 4500.0]
    expected_ends = [900.0, 1800.0, 2700.0, 3600.0, 4500.0, 5400.0]
    
    for idx, seg in enumerate(segments):
        assert seg.part_number == idx + 1
        assert seg.start_time == expected_starts[idx]
        assert seg.end_time == expected_ends[idx]
        assert seg.duration == 900.0
        assert seg.filename == f"part_{(idx + 1):03d}.mp4"

def test_equal_split_non_divisible():
    # 100 seconds into 3 parts -> ~33.333s each
    segments = EqualSplitService.calculate_splits(duration=100.0, parts=3)
    assert len(segments) == 3
    assert segments[0].start_time == 0.0
    assert segments[-1].end_time == 100.0

def test_equal_split_invalid_inputs():
    with pytest.raises(ValueError):
        EqualSplitService.calculate_splits(duration=-10.0, parts=4)
    with pytest.raises(ValueError):
        EqualSplitService.calculate_splits(duration=100.0, parts=1)
