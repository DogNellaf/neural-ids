from unittest.mock import MagicMock
from tests.conftest import *  # noqa

from packet_count import PacketCount
from packet_direction import PacketDirection


def _build_feature(packets_with_dir):
    """Строит заглушку flow.packets."""
    feature = MagicMock()
    feature.packets = packets_with_dir
    return feature


class TestPacketCount:
    def test_get_total_all(self):
        fwd = make_packet(size=100, time=0.0)
        rev = make_packet(size=80, time=0.1)
        feature = _build_feature([
            (fwd, PacketDirection.FORWARD),
            (rev, PacketDirection.REVERSE),
        ])
        pc = PacketCount(feature)
        assert pc.get_total() == 2

    def test_get_total_by_direction(self):
        fwd = make_packet(size=100, time=0.0)
        rev = make_packet(size=80, time=0.1)
        feature = _build_feature([
            (fwd, PacketDirection.FORWARD),
            (rev, PacketDirection.REVERSE),
        ])
        pc = PacketCount(feature)
        assert pc.get_total(PacketDirection.FORWARD) == 1
        assert pc.get_total(PacketDirection.REVERSE) == 1

    def test_get_total_empty(self):
        feature = _build_feature([])
        pc = PacketCount(feature)
        assert pc.get_total() == 0

    def test_get_rate_zero_duration(self):
        # Один пакет => duration==0
        p = make_packet(size=100, time=1.0)
        feature = _build_feature([(p, PacketDirection.FORWARD)])
        feature.start_timestamp = 1.0
        feature.latest_timestamp = 1.0
        pc = PacketCount(feature)
        assert pc.get_rate() == 0

    def test_get_down_up_ratio_no_forward(self):
        feature = _build_feature([])
        pc = PacketCount(feature)
        assert pc.get_down_up_ratio() == 0

    def test_get_down_up_ratio(self):
        fwd1 = make_packet(time=0.0)
        fwd2 = make_packet(time=0.1)
        rev = make_packet(time=0.2)
        feature = _build_feature([
            (fwd1, PacketDirection.FORWARD),
            (fwd2, PacketDirection.FORWARD),
            (rev, PacketDirection.REVERSE),
        ])
        pc = PacketCount(feature)
        assert pc.get_down_up_ratio() == 0.5

    def test_get_payload_tcp(self):
        payload = b"hello"
        packet = make_packet(protocol="TCP", payload=payload)
        result = PacketCount.get_payload(packet)
        assert result == payload

    def test_get_payload_udp(self):
        payload = b"data"
        packet = make_packet(protocol="UDP", payload=payload)
        result = PacketCount.get_payload(packet)
        assert result == payload

    def test_get_payload_no_transport_returns_bytes(self):
        packet = make_packet(protocol="TCP")
        packet.__contains__ = lambda self, key: False
        result = PacketCount.get_payload(packet)
        assert result == b""
        assert isinstance(result, bytes)

    def test_has_payload_counts_correctly(self):
        p_with = make_packet(protocol="TCP", payload=b"data", time=0.0)
        p_empty = make_packet(protocol="TCP", payload=b"", time=0.1)
        feature = _build_feature([
            (p_with, PacketDirection.FORWARD),
            (p_empty, PacketDirection.FORWARD),
        ])
        pc = PacketCount(feature)
        assert pc.has_payload() == 1
        assert pc.has_payload(PacketDirection.FORWARD) == 1
        assert pc.has_payload(PacketDirection.REVERSE) == 0
