from packet_direction import PacketDirection
from packet_time import PacketTime


class PacketCount:
    """This class extracts features related to the Packet Count."""

    def __init__(self, feature):
        self.feature = feature

    def get_total(self, packet_direction=None) -> int:
        if packet_direction is not None:
            return sum(
                1 for _, direction in self.feature.packets
                if direction == packet_direction
            )
        return len(self.feature.packets)

    def get_rate(self, packet_direction=None) -> float:
        duration = PacketTime(self.feature).get_duration()
        if duration == 0:
            return 0
        return self.get_total(packet_direction) / duration

    def get_down_up_ratio(self) -> float:
        forward = self.get_total(PacketDirection.FORWARD)
        backward = self.get_total(PacketDirection.REVERSE)
        if forward > 0:
            return backward / forward
        return 0

    @staticmethod
    def get_payload(packet):
        if "TCP" in packet:
            return packet["TCP"].payload
        elif "UDP" in packet:
            return packet["UDP"].payload
        return b""

    def has_payload(self, packet_direction=None) -> int:
        if packet_direction is not None:
            return sum(
                1 for packet, direction in self.feature.packets
                if direction == packet_direction and len(self.get_payload(packet)) > 0
            )
        return sum(
            1 for packet, _ in self.feature.packets
            if len(self.get_payload(packet)) > 0
        )
