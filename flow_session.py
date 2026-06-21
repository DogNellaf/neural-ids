import logging
import subprocess

import neural
import pandas as pd
import db

from collections import defaultdict
from scapy.sessions import DefaultSession
from packet_direction import PacketDirection
from packet_flow_key import get_packet_flow_key
from flow import Flow

from settings import (
    ATTACKS, NOT_ATTACK, EXPIRED_UPDATE, GARBAGE_COLLECT_PACKETS,
    IS_DEBUG, FLOW_DURATION, PACKET_DURATION,
)

logger = logging.getLogger(__name__)


class FlowSession(DefaultSession):

    def __init__(self, *args, **kwargs):
        self.flows = {}
        self.csv_line = 0
        self.packets_count = 0
        self.packets = []  # буфер потоков для батчевого предсказания
        self.clumped_flows_per_label = defaultdict(list)
        super(FlowSession, self).__init__(*args, **kwargs)

    def toPacketList(self):
        self.garbage_collect(None)
        return super(FlowSession, self).toPacketList()

    def on_packet_received(self, packet):
        count = 0
        direction = PacketDirection.FORWARD

        try:
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get((packet_flow_key, count))
        except Exception:
            return

        self.packets_count += 1

        if flow is None:
            direction = PacketDirection.REVERSE
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get((packet_flow_key, count))

        if flow is None:
            direction = PacketDirection.FORWARD
            flow = Flow(packet, direction)
            packet_flow_key = get_packet_flow_key(packet, direction)
            self.flows[(packet_flow_key, count)] = flow

        elif (packet.time - flow.latest_timestamp) > EXPIRED_UPDATE:
            expired = EXPIRED_UPDATE
            while (packet.time - flow.latest_timestamp) > expired:
                count += 1
                expired += EXPIRED_UPDATE
                flow = self.flows.get((packet_flow_key, count))

                if flow is None:
                    flow = Flow(packet, direction)
                    self.flows[(packet_flow_key, count)] = flow
                    break

        elif "TCP" in packet and packet["TCP"].flags.F:
            # FIN — соединение завершается, обрабатываем поток немедленно
            flow.add_packet(packet, direction)
            self.garbage_collect(packet.time)
            return

        flow.add_packet(packet, direction)

        if self.packets_count % GARBAGE_COLLECT_PACKETS == 0 or flow.duration > FLOW_DURATION:
            self.garbage_collect(packet.time)

    def block_connection(self, ip: str, port: int) -> None:
        """Блокирует входящее соединение через Windows Firewall."""
        rule_name = f"IDS Block {ip}:{port}"
        command = (
            f'New-NetFirewallRule -DisplayName "{rule_name}" '
            f'-Direction Inbound -LocalPort {port} -Protocol TCP '
            f'-RemoteAddress {ip} -Action Block'
        )
        try:
            subprocess.run(
                ['powershell', '-Command', command],
                check=True,
                capture_output=True,
            )
            logger.info("Соединение с %s:%s заблокировано.", ip, port)
        except subprocess.CalledProcessError as e:
            logger.error("Не удалось заблокировать %s:%s — %s", ip, port, e.stderr)

    def garbage_collect(self, latest_time) -> None:
        keys = list(self.flows.keys())
        for k in keys:
            flow = self.flows.get(k)
            if flow is None:
                continue

            # Пропускаем активные потоки, которые ещё не истекли
            if (
                latest_time is not None
                and (latest_time - flow.latest_timestamp) < EXPIRED_UPDATE
                and flow.duration < FLOW_DURATION
            ):
                continue

            data = flow.get_data()
            self.packets.append(data)

            if len(self.packets) % PACKET_DURATION == 0:
                self._process_batch(flow)

            del self.flows[k]

    def _process_batch(self, last_flow) -> None:
        """Запускает предсказание нейросети для текущего батча потоков."""
        try:
            predict = pd.DataFrame(neural.predict(self.packets)).T

            if IS_DEBUG:
                debug_df = predict.copy()
                debug_df[0] = (debug_df[0] * 100).round() / 100
                debug_df['attack'] = ATTACKS
                logger.debug("Предсказание нейронной сети:\n%s", debug_df[debug_df[0] > 0])

            index = int(predict.idxmax()[0])
            attack_title = ATTACKS[index]

            if attack_title == NOT_ATTACK:
                logger.info("Атака не обнаружена.")
            else:
                logger.warning("Обнаружена атака: %s", attack_title)
                batch = list(self.packets)
                for i in range(min(5, len(batch))):
                    batch[i] = dict(batch[i])
                    batch[i]['src_ip'] = f"{last_flow.src_ip}:{last_flow.src_port}"
                    batch[i]['dst_ip'] = f"{last_flow.dest_ip}:{last_flow.dest_port}"
                db.save_attack(batch, attack_title)
                self.block_connection(last_flow.src_ip, last_flow.src_port)

        except Exception:
            logger.exception("Ошибка при обработке батча пакетов.")
        finally:
            self.packets = []


def generate_session_class():
    return type(
        "NewFlowSession",
        (FlowSession,),
        {
            "output_mode": "flow",
            "output_file": None,
            "url_model": None,
        },
    )
