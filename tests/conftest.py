"""Общие фикстуры и моки для тестов NeuralIDS."""
import sys
import os
from unittest.mock import MagicMock

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Заглушки для тяжёлых зависимостей ──────────────────────────────────────
# Мокаем scapy до его импорта в тестируемых модулях
_scapy_mock = MagicMock()
sys.modules.setdefault("scapy", _scapy_mock)
sys.modules.setdefault("scapy.sendrecv", _scapy_mock)
sys.modules.setdefault("scapy.sessions", _scapy_mock)
sys.modules.setdefault("scapy.layers", _scapy_mock)
sys.modules.setdefault("scapy.layers.inet", _scapy_mock)

# Мокаем keras/tensorflow
_keras_mock = MagicMock()
sys.modules.setdefault("keras", _keras_mock)
sys.modules.setdefault("keras.models", _keras_mock)
sys.modules.setdefault("tensorflow", MagicMock())

# Мокаем psycopg2
sys.modules.setdefault("psycopg2", MagicMock())
sys.modules.setdefault("psycopg2.extras", MagicMock())

# Мокаем PyQt5
_qt_mock = MagicMock()
for _mod in [
    "PyQt5", "PyQt5.QtWidgets", "PyQt5.QtCore", "PyQt5.QtGui",
]:
    sys.modules.setdefault(_mod, _qt_mock)


def make_packet(
    src_ip="192.168.1.1",
    dst_ip="192.168.1.2",
    src_port=12345,
    dst_port=80,
    protocol="TCP",
    size=100,
    time=0.0,
    flags=None,
    window=65535,
    payload=b"",
    ihl=5,
):
    """Фабрика мок-пакетов scapy."""
    packet = MagicMock()
    packet.__len__ = MagicMock(return_value=size)
    packet.time = time
    packet.proto = 6 if protocol == "TCP" else 17

    ip_layer = MagicMock()
    ip_layer.src = src_ip
    ip_layer.dst = dst_ip
    ip_layer.ihl = ihl
    packet.__getitem__ = MagicMock(side_effect=lambda key: {
        "IP": ip_layer,
        "TCP": _make_tcp(src_port, dst_port, window, flags, payload) if protocol == "TCP" else None,
        "UDP": _make_udp(src_port, dst_port, payload) if protocol == "UDP" else None,
    }.get(key, MagicMock()))

    packet.__contains__ = MagicMock(side_effect=lambda key: key == "IP" or key == protocol)

    # Симулируем packet.flags как IP-флаги (не TCP)
    packet.flags = MagicMock()

    return packet


def _make_tcp(sport, dport, window, flags, payload):
    tcp = MagicMock()
    tcp.sport = sport
    tcp.dport = dport
    tcp.window = window
    tcp.payload = payload
    flag_obj = MagicMock()
    flag_obj.F = bool(flags and "F" in flags)
    flag_obj.S = bool(flags and "S" in flags)
    flag_obj.R = bool(flags and "R" in flags)
    flag_obj.P = bool(flags and "P" in flags)
    flag_obj.A = bool(flags and "A" in flags)
    flag_obj.U = bool(flags and "U" in flags)
    flag_obj.E = bool(flags and "E" in flags)
    flag_obj.__str__ = MagicMock(return_value=flags or "")
    tcp.flags = flag_obj
    return tcp


def _make_udp(sport, dport, payload):
    udp = MagicMock()
    udp.sport = sport
    udp.dport = dport
    udp.payload = payload
    return udp
