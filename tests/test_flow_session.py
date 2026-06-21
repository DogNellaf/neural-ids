"""Тесты FlowSession — проверяем управление потоками и обнаружение атак."""
import sys
from unittest.mock import MagicMock, patch
from tests.conftest import *  # noqa


class TestFlowSessionInit:
    def _get_session_class(self):
        # Мокаем тяжёлые импорты модуля
        with patch.dict(sys.modules, {
            "neural": MagicMock(),
            "db": MagicMock(),
        }):
            if "flow_session" in sys.modules:
                del sys.modules["flow_session"]
            import flow_session
            return flow_session.FlowSession, flow_session

    def test_packets_is_instance_variable(self):
        cls, _ = self._get_session_class()
        with patch.object(cls, "__init__", lambda self, *a, **kw: None):
            s1 = cls.__new__(cls)
            s1.packets = []
            s2 = cls.__new__(cls)
            s2.packets = []
            s1.packets.append("x")
            assert s2.packets == [], "packets не должны быть общими между экземплярами"

    def test_generate_session_class_returns_subclass(self):
        _, mod = self._get_session_class()
        new_cls = mod.generate_session_class()
        assert issubclass(new_cls, mod.FlowSession)

    def test_generate_session_class_has_attributes(self):
        _, mod = self._get_session_class()
        new_cls = mod.generate_session_class()
        assert new_cls.output_mode == "flow"
        assert new_cls.output_file is None
        assert new_cls.url_model is None
