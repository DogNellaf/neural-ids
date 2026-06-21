from unittest.mock import MagicMock
from tests.conftest import *  # noqa

from packet_time import PacketTime
from packet_direction import PacketDirection


def _flow_with_packets(times, direction=PacketDirection.FORWARD):
    packets = []
    for t in times:
        p = make_packet(time=t)
        packets.append((p, direction))
    flow = MagicMock()
    flow.packets = packets
    return flow


class TestPacketTime:
    def test_get_duration_single_packet(self):
        flow = _flow_with_packets([1.0])
        pt = PacketTime(flow)
        assert pt.get_duration() == 0.0

    def test_get_duration_multiple(self):
        flow = _flow_with_packets([1.0, 1.5, 2.0])
        pt = PacketTime(flow)
        assert abs(pt.get_duration() - 1.0) < 1e-9

    def test_get_duration_empty(self):
        flow = MagicMock()
        flow.packets = []
        pt = PacketTime(flow)
        assert pt.get_duration() == 0

    def test_get_time_stamp_format(self):
        import time
        now = time.time()
        flow = _flow_with_packets([now])
        pt = PacketTime(flow)
        ts = pt.get_time_stamp()
        assert len(ts) == 19  # "YYYY-MM-DD HH:MM:SS"

    def test_get_time_stamp_empty(self):
        flow = MagicMock()
        flow.packets = []
        pt = PacketTime(flow)
        assert pt.get_time_stamp() == ""

    def test_get_packet_iat(self):
        flow = _flow_with_packets([0.0, 1.0, 3.0])
        pt = PacketTime(flow)
        iat = pt.get_packet_iat()
        assert len(iat) == 2
        assert abs(iat[0] - 1e6) < 1  # 1 sec in microseconds
        assert abs(iat[1] - 2e6) < 1

    def test_get_packet_iat_single(self):
        flow = _flow_with_packets([0.0])
        pt = PacketTime(flow)
        assert pt.get_packet_iat() == []

    def test_get_mean_empty(self):
        flow = MagicMock()
        flow.packets = []
        pt = PacketTime(flow)
        assert pt.get_mean() == 0.0

    def test_get_std_empty(self):
        flow = MagicMock()
        flow.packets = []
        pt = PacketTime(flow)
        assert pt.get_std() == 0.0

    def test_get_var_single_packet(self):
        flow = _flow_with_packets([5.0])
        pt = PacketTime(flow)
        assert pt.get_var() == 0.0

    def test_get_cov_zero_mean(self):
        flow = _flow_with_packets([1.0])
        pt = PacketTime(flow)
        # mean будет 0 (все относительные времена = 0 при одном пакете)
        assert pt.get_cov() == -1

    def test_relative_time_list(self):
        flow = _flow_with_packets([0.0, 1.0, 2.0])
        pt = PacketTime(flow)
        rel = pt.relative_time_list()
        assert rel[0] == 0
        assert len(rel) == 3
