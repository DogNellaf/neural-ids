from datetime import datetime

import numpy
from scipy import stats as stat


class PacketTime:
    """This class extracts features related to the Packet Times."""

    def __init__(self, flow):
        self.flow = flow
        self._packet_times = None

    def _get_packet_times(self) -> list:
        if self._packet_times is not None:
            return self._packet_times
        if not self.flow.packets:
            return []
        first_packet_time = self.flow.packets[0][0].time
        self._packet_times = [
            float(packet.time - first_packet_time)
            for packet, _ in self.flow.packets
        ]
        return self._packet_times

    def get_packet_iat(self, packet_direction=None) -> list:
        if packet_direction is not None:
            packets = [
                packet for packet, direction in self.flow.packets
                if direction == packet_direction
            ]
        else:
            packets = [packet for packet, _ in self.flow.packets]

        return [
            1e6 * float(packets[i].time - packets[i - 1].time)
            for i in range(1, len(packets))
        ]

    def relative_time_list(self) -> list:
        packet_times = self._get_packet_times()
        result = []
        for index, time in enumerate(packet_times):
            if index == 0:
                result.append(0)
            elif index < 50:
                result.append(float(time - packet_times[index - 1]))
            else:
                break
        return result

    def get_time_stamp(self) -> str:
        if not self.flow.packets:
            return ""
        time = self.flow.packets[0][0].time
        return datetime.fromtimestamp(float(time)).strftime("%Y-%m-%d %H:%M:%S")

    def get_duration(self) -> float:
        times = self._get_packet_times()
        if not times:
            return 0
        return max(times) - min(times)

    def get_var(self) -> float:
        times = self._get_packet_times()
        return float(numpy.var(times)) if times else 0.0

    def get_std(self) -> float:
        return float(numpy.sqrt(self.get_var()))

    def get_mean(self) -> float:
        times = self._get_packet_times()
        return float(numpy.mean(times)) if times else 0.0

    def get_median(self) -> float:
        times = self._get_packet_times()
        return float(numpy.median(times)) if times else 0.0

    def get_mode(self) -> float:
        times = self._get_packet_times()
        if not times:
            return -1
        return float(stat.mode(times)[0])

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
