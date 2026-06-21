from tests.conftest import *  # noqa

from packet_direction import PacketDirection


class TestPacketDirection:
    def test_forward_and_reverse_are_different(self):
        assert PacketDirection.FORWARD != PacketDirection.REVERSE

    def test_enum_values(self):
        assert PacketDirection.FORWARD.value == 1
        assert PacketDirection.REVERSE.value == 2

    def test_membership(self):
        assert PacketDirection.FORWARD in PacketDirection
        assert PacketDirection.REVERSE in PacketDirection
