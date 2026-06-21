from unittest.mock import MagicMock
from tests.conftest import *  # noqa

from flag_count import FlagCount
from packet_direction import PacketDirection


def _feature_with_flags(flag_strings_and_dirs):
    """flag_strings_and_dirs: list of (flag_str, direction)."""
    packets = []
    for flag_str, direction in flag_strings_and_dirs:
        p = make_packet(flags=flag_str, protocol="TCP")
        packets.append((p, direction))
    feature = MagicMock()
    feature.packets = packets
    return feature


class TestFlagCount:
    def test_has_syn_flag(self):
        feature = _feature_with_flags([("S", PacketDirection.FORWARD)])
        fc = FlagCount(feature)
        assert fc.has_flag("SYN") == 1

    def test_has_no_syn_flag(self):
        feature = _feature_with_flags([("A", PacketDirection.FORWARD)])
        fc = FlagCount(feature)
        assert fc.has_flag("SYN") == 0

    def test_has_flag_by_direction_forward(self):
        feature = _feature_with_flags([
            ("P", PacketDirection.FORWARD),
            ("A", PacketDirection.REVERSE),
        ])
        fc = FlagCount(feature)
        assert fc.has_flag("PSH", PacketDirection.FORWARD) == 1
        assert fc.has_flag("PSH", PacketDirection.REVERSE) == 0

    def test_has_flag_by_direction_reverse(self):
        feature = _feature_with_flags([
            ("A", PacketDirection.FORWARD),
            ("U", PacketDirection.REVERSE),
        ])
        fc = FlagCount(feature)
        assert fc.has_flag("URG", PacketDirection.REVERSE) == 1
        assert fc.has_flag("URG", PacketDirection.FORWARD) == 0

    def test_has_flag_empty_packets(self):
        feature = MagicMock()
        feature.packets = []
        fc = FlagCount(feature)
        assert fc.has_flag("FIN") == 0

    def test_has_fin_flag(self):
        feature = _feature_with_flags([("F", PacketDirection.FORWARD)])
        fc = FlagCount(feature)
        assert fc.has_flag("FIN") == 1

    def test_has_multiple_flags(self):
        feature = _feature_with_flags([("FA", PacketDirection.FORWARD)])
        fc = FlagCount(feature)
        assert fc.has_flag("FIN") == 1
        assert fc.has_flag("ACK") == 1
        assert fc.has_flag("SYN") == 0
