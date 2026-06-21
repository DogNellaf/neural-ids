import pytest
from tests.conftest import *  # noqa

from packet_flow_key import get_packet_flow_key
from packet_direction import PacketDirection


class TestGetPacketFlowKey:
    def test_tcp_forward(self):
        packet = make_packet(
            src_ip="1.2.3.4", dst_ip="5.6.7.8",
            src_port=1234, dst_port=80, protocol="TCP",
        )
        dest_ip, src_ip, src_port, dest_port = get_packet_flow_key(packet, PacketDirection.FORWARD)
        assert src_ip == "1.2.3.4"
        assert dest_ip == "5.6.7.8"
        assert src_port == 1234
        assert dest_port == 80

    def test_tcp_reverse(self):
        packet = make_packet(
            src_ip="1.2.3.4", dst_ip="5.6.7.8",
            src_port=1234, dst_port=80, protocol="TCP",
        )
        dest_ip, src_ip, src_port, dest_port = get_packet_flow_key(packet, PacketDirection.REVERSE)
        assert src_ip == "5.6.7.8"
        assert dest_ip == "1.2.3.4"
        assert src_port == 80
        assert dest_port == 1234

    def test_udp_forward(self):
        packet = make_packet(
            src_ip="10.0.0.1", dst_ip="10.0.0.2",
            src_port=5000, dst_port=53, protocol="UDP",
        )
        dest_ip, src_ip, src_port, dest_port = get_packet_flow_key(packet, PacketDirection.FORWARD)
        assert src_port == 5000
        assert dest_port == 53

    def test_unsupported_protocol_raises(self):
        packet = make_packet(protocol="TCP")
        # Mок, не содержащий ни TCP ни UDP
        packet.__contains__ = lambda self, key: key == "IP"
        with pytest.raises(Exception, match="Only TCP protocols are supported"):
            get_packet_flow_key(packet, PacketDirection.FORWARD)
