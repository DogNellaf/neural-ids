import numpy
from scipy import stats as stat


class PacketLength:
    """This class extracts features related to the Packet Lengths."""

    def __init__(self, feature):
        self.feature = feature

    def get_packet_length(self, packet_direction=None) -> list:
        if packet_direction is not None:
            return [
                len(packet) for packet, direction in self.feature.packets
                if direction == packet_direction
            ]
        return [len(packet) for packet, _ in self.feature.packets]

    def get_header_length(self, packet_direction=None):
        if packet_direction is not None:
            return (
                packet["IP"].ihl * 4 for packet, direction in self.feature.packets
                if direction == packet_direction
            )
        return (packet["IP"].ihl * 4 for packet, _ in self.feature.packets)

    def get_total_header(self, packet_direction=None) -> int:
        return sum(self.get_header_length(packet_direction))

    def get_min_header(self, packet_direction=None) -> int:
        lengths = list(self.get_header_length(packet_direction))
        return min(lengths) if lengths else 0

    def get_max(self, packet_direction=None) -> int:
        lengths = self.get_packet_length(packet_direction)
        return max(lengths) if lengths else 0

    def get_min(self, packet_direction=None) -> int:
        lengths = self.get_packet_length(packet_direction)
        return min(lengths) if lengths else 0

    def get_total(self, packet_direction=None) -> int:
        return sum(self.get_packet_length(packet_direction))

    def get_avg(self, packet_direction=None) -> float:
        lengths = self.get_packet_length(packet_direction)
        return sum(lengths) / len(lengths) if lengths else 0.0

    def first_fifty(self) -> list:
        return self.get_packet_length()[:50]

    def get_var(self, packet_direction=None) -> float:
        lengths = self.get_packet_length(packet_direction)
        return float(numpy.var(lengths)) if lengths else 0.0

    def get_std(self, packet_direction=None) -> float:
        return float(numpy.sqrt(self.get_var(packet_direction)))

    def get_mean(self, packet_direction=None) -> float:
        lengths = self.get_packet_length(packet_direction)
        return float(numpy.mean(lengths)) if lengths else 0.0

    def get_median(self) -> float:
        lengths = self.get_packet_length()
        return float(numpy.median(lengths)) if lengths else 0.0

    def get_mode(self) -> float:
        lengths = self.get_packet_length()
        if not lengths:
            return -1
        return int(stat.mode(lengths)[0])

    def get_skew(self) -> float:
        std = self.get_std()
        if std == 0:
            return -10
        return 3 * (self.get_mean() - self.get_median()) / std

    def get_skew2(self) -> float:
        std = self.get_std()
        if std == 0:
            return -10
        return (self.get_mean() - self.get_mode()) / std

    def get_cov(self) -> float:
        mean = self.get_mean()
        if mean == 0:
            return -1
        return self.get_std() / mean
