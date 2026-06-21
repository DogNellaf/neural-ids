from unittest.mock import MagicMock
from tests.conftest import *  # noqa

from packet_length import PacketLength
from packet_direction import PacketDirection


def _feature(packets):
    f = MagicMock()
    f.packets = packets
    return f


class TestPacketLength:
    def _make_packets(self, sizes, direction=PacketDirection.FORWARD):
        result = []
        for i, size in enumerate(sizes):
            p = make_packet(size=size, time=float(i) * 0.1)
            result.append((p, direction))
        return result

    def test_get_packet_length_all(self):
        packets = self._make_packets([100, 200, 300])
        pl = PacketLength(_feature(packets))
        assert pl.get_packet_length() == [100, 200, 300]

    def test_get_packet_length_by_direction(self):
        fwd = self._make_packets([100, 200], PacketDirection.FORWARD)
        rev = self._make_packets([50], PacketDirection.REVERSE)
        pl = PacketLength(_feature(fwd + rev))
        assert pl.get_packet_length(PacketDirection.FORWARD) == [100, 200]
        assert pl.get_packet_length(PacketDirection.REVERSE) == [50]

    def test_get_max_empty(self):
        pl = PacketLength(_feature([]))
        assert pl.get_max() == 0

    def test_get_min_empty(self):
        pl = PacketLength(_feature([]))
        assert pl.get_min() == 0

    def test_get_max(self):
        packets = self._make_packets([50, 100, 75])
        pl = PacketLength(_feature(packets))
        assert pl.get_max() == 100

    def test_get_min(self):
        packets = self._make_packets([50, 100, 75])
        pl = PacketLength(_feature(packets))
        assert pl.get_min() == 50

    def test_get_total(self):
        packets = self._make_packets([100, 200])
        pl = PacketLength(_feature(packets))
        assert pl.get_total() == 300

    def test_get_avg(self):
        packets = self._make_packets([100, 200, 300])
        pl = PacketLength(_feature(packets))
        assert abs(pl.get_avg() - 200.0) < 1e-9

    def test_get_avg_empty(self):
        pl = PacketLength(_feature([]))
        assert pl.get_avg() == 0.0

    def test_get_var_empty(self):
        pl = PacketLength(_feature([]))
        assert pl.get_var() == 0.0

    def test_get_std(self):
        packets = self._make_packets([2, 4, 4, 4, 5, 5, 7, 9])
        pl = PacketLength(_feature(packets))
        assert pl.get_std() > 0

    def test_get_mean_empty(self):
        pl = PacketLength(_feature([]))
        assert pl.get_mean() == 0.0

    def test_get_mean(self):
        packets = self._make_packets([10, 20, 30])
        pl = PacketLength(_feature(packets))
        assert abs(pl.get_mean() - 20.0) < 1e-9

    def test_first_fifty(self):
        packets = self._make_packets(list(range(60)))
        pl = PacketLength(_feature(packets))
        assert len(pl.first_fifty()) == 50

    def test_get_cov_zero_mean(self):
        pl = PacketLength(_feature([]))
        assert pl.get_cov() == -1
