import logging
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"

from scapy.sendrecv import AsyncSniffer
from flow_session import generate_session_class
from settings import INTERNET_INTERFACE

logger = logging.getLogger(__name__)


def create_sniffer(input_interface: str) -> AsyncSniffer:
    session = generate_session_class()
    return AsyncSniffer(
        iface=input_interface,
        filter="ip and (tcp or udp)",
        prn=None,
        session=session,
        store=False,
    )


def main():
    sniffer = create_sniffer(INTERNET_INTERFACE)
    sniffer.start()
    logger.info("Сниффер запущен на интерфейсе '%s'.", INTERNET_INTERFACE)
    print("Система запущена")
    try:
        sniffer.join()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, останавливаю сниффер...")
        sniffer.stop()
    finally:
        sniffer.join()
        logger.info("Сниффер остановлен.")
