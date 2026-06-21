from unittest.mock import MagicMock, patch
from tests.conftest import *  # noqa

from flow_bytes import FlowBytes
from packet_direction import PacketDirection


def _feature(packets, fwd_bulk_count=0, bwd_bulk_count=0,
             fwd_bulk_size=0, bwd_bulk_size=0,
             fwd_bulk_pkt=0, bwd_bulk_pkt=0,
             fwd_bulk_dur=0, bwd_bulk_dur=0):
    f = MagicMock()
    f.packets = packets
    f.forward_bulk_count = fwd_bulk_count
    f.backward_bulk_count = bwd_bulk_count
    f.forward_bulk_size = fwd_bulk_size
    f.backward_bulk_size = bwd_bulk_size
    f.forward_bulk_packet_count = fwd_bulk_pkt
    f.backward_bulk_packet_count = bwd_bulk_pkt
    f.forward_bulk_duration = fwd_bulk_dur
    f.backward_bulk_duration = bwd_bulk_dur
    f.start_timestamp = 0.0
    f.latest_timestamp = 1.0
    return f


class TestFlowBytes:
    def test_get_bytes_empty(self):
        fb = FlowBytes(_feature([]))
        assert fb.get_bytes() == 0

    def test_get_bytes(self):
        p1 = make_packet(size=100, time=0.0)
        p2 = make_packet(size=200, time=0.5)
        feat = _feature([(p1, PacketDirection.FORWARD), (p2, PacketDirection.REVERSE)])
        fb = FlowBytes(feat)
        assert fb.get_bytes() == 300

    def test_get_rate_zero_duration(self):
        p = make_packet(size=100, time=0.0)
        feat = _feature([(p, PacketDirection.FORWARD)])
        feat.start_timestamp = 0.0
        feat.latest_timestamp = 0.0
        # PacketTime.get_duration() returns 0 for single packet
        fb = FlowBytes(feat)
        assert fb.get_rate() == 0

    def test_get_bytes_per_bulk_forward_zero_count(self):
        fb = FlowBytes(_feature([], fwd_bulk_count=0))
        assert fb.get_bytes_per_bulk(PacketDirection.FORWARD) == 0

    def test_get_bytes_per_bulk_forward(self):
        fb = FlowBytes(_feature([], fwd_bulk_count=2, fwd_bulk_size=100))
        assert fb.get_bytes_per_bulk(PacketDirection.FORWARD) == 50.0

    def test_get_bytes_per_bulk_reverse(self):
        fb = FlowBytes(_feature([], bwd_bulk_count=4, bwd_bulk_size=200))
        assert fb.get_bytes_per_bulk(PacketDirection.REVERSE) == 50.0

    def test_get_packets_per_bulk_zero_count(self):
        fb = FlowBytes(_feature([]))
        assert fb.get_packets_per_bulk(PacketDirection.FORWARD) == 0

    def test_get_packets_per_bulk(self):
        fb = FlowBytes(_feature([], fwd_bulk_count=2, fwd_bulk_pkt=8))
        assert fb.get_packets_per_bulk(PacketDirection.FORWARD) == 4.0

    def test_get_bulk_rate_zero_duration(self):
        fb = FlowBytes(_feature([], fwd_bulk_dur=0))
        assert fb.get_bulk_rate(PacketDirection.FORWARD) == 0

    def test_get_bulk_rate(self):
        fb = FlowBytes(_feature([], fwd_bulk_dur=2.0, fwd_bulk_size=1000))
        assert fb.get_bulk_rate(PacketDirection.FORWARD) == 500.0

    def test_get_min_forward_header_bytes_empty(self):
        fb = FlowBytes(_feature([]))
        assert fb.get_min_forward_header_bytes() == 0
