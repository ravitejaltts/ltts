import sys

# if not sys.platform.startswith('darwin'):
#     # Skip on MAC as cantools is not available

# non_mac = pytest.mark.skipif(
#     sys.platform.startswith('darwin'),
#     reason="cantools module not available on MAC"
# )

from can_service.can_helper import (
    clean_pgn,
    increment_stats
)




def test_clean_pgn():
    # Esnure we get correct clean pgns cleaned of priority and source address
    assert clean_pgn(0xffffffff) == 0x01FFFF00
    assert clean_pgn(0x00123444) == 0x00123400


def test_stats():
    stats = {}
    increment_stats(0x01F21100, stats)
    assert stats.get('01F21100') == 1
    increment_stats(0x01F21100, stats)
    assert stats.get('01F21100') == 2

    increment_stats(0x01F21101, stats)
    assert stats.get('01F21101') == 1

    increment_stats(0x01F21100, stats)
    assert stats.get('01F21100') == 3

    increment_stats(0x01F21102, stats)
    assert stats.get('01F21102') == 1

    increment_stats(0x01F21101, stats)
    assert stats.get('01F21101') == 2
