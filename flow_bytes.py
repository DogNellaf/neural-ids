from scapy.layers.inet import IP, TCP

from packet_direction import PacketDirection
from packet_time import PacketTime


class FlowBytes:
    """Extracts features from the traffic related to the bytes in a flow."""

    def __init__(self, feature):
        self.feature = feature

    def get_bytes(self) -> int:
        return sum(len(packet) for packet, _ in self.feature.packets)

    def get_rate(self) -> float:
        duration = PacketTime(self.feature).get_duration()
        if duration == 0:
            return 0
        return self.get_bytes() / duration

    def _header_size(self, packet) -> int:
        return packet[IP].ihl * 4 if TCP in packet else 8

    def get_forward_header_bytes(self) -> int:
        return sum(
            self._header_size(packet)
            for packet, direction in self.feature.packets
            if direction == PacketDirection.FORWARD
        )

    def get_reverse_header_bytes(self) -> int:
        return sum(
            self._header_size(packet)
            for packet, direction in self.feature.packets
            if direction == PacketDirection.REVERSE
        )

    def get_min_forward_header_bytes(self) -> int:
        sizes = [
            self._header_size(packet)
            for packet, direction in self.feature.packets
            if direction == PacketDirection.FORWARD
        ]
        return min(sizes) if sizes else 0

    def get_bytes_per_bulk(self, packet_direction) -> float:
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_count != 0:
                return self.feature.forward_bulk_size / self.feature.forward_bulk_count
        else:
            if self.feature.backward_bulk_count != 0:
                return self.feature.backward_bulk_size / self.feature.backward_bulk_count
        return 0

    def get_packets_per_bulk(self, packet_direction) -> float:
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_count != 0:
                return self.feature.forward_bulk_packet_count / self.feature.forward_bulk_count
        else:
            if self.feature.backward_bulk_count != 0:
                return self.feature.backward_bulk_packet_count / self.feature.backward_bulk_count
        return 0

    def get_bulk_rate(self, packet_direction) -> float:
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_duration != 0:
                return self.feature.forward_bulk_size / self.feature.forward_bulk_duration
        else:
            if self.feature.backward_bulk_duration != 0:
                return self.feature.backward_bulk_size / self.feature.backward_bulk_duration
        return 0
