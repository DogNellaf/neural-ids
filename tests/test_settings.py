"""Тесты конфигурации settings.py."""
import os
import sys
from tests.conftest import *  # noqa


class TestSettings:
    def _reload(self, env=None):
        env = env or {}
        with patch_env(env):
            if "settings" in sys.modules:
                del sys.modules["settings"]
            import settings
            return settings

    def test_not_attack_is_first_in_attacks(self):
        import settings
        assert settings.NOT_ATTACK == settings.ATTACKS[0]
        assert settings.NOT_ATTACK == "Benign"

    def test_expired_update_is_single_value(self):
        import settings
        # Убеждаемся, что дублирование устранено — значение 240
        assert settings.EXPIRED_UPDATE == 240

    def test_excluded_columns_contains_src_port(self):
        import settings
        assert "src_port" in settings.EXCLUDED_COLUMNS

    def test_excluded_columns_contains_ip_and_timestamp(self):
        import settings
        assert "src_ip" in settings.EXCLUDED_COLUMNS
        assert "dst_ip" in settings.EXCLUDED_COLUMNS
        assert "timestamp" in settings.EXCLUDED_COLUMNS

    def test_window_dimensions_positive(self):
        import settings
        assert settings.WINDOW_WIDTH > 0
        assert settings.WINDOW_HEIGHT > 0

    def test_timer_interval_positive(self):
        import settings
        assert settings.TIMER_INTERVAL > 0

    def test_attacks_list_not_empty(self):
        import settings
        assert len(settings.ATTACKS) > 0

    def test_no_empty_attack_title(self):
        import settings
        for attack in settings.ATTACKS:
            assert attack != "", f"Пустое название атаки в списке ATTACKS: {settings.ATTACKS}"


def patch_env(env: dict):
    """Контекстный менеджер для временной замены переменных окружения."""
    import unittest.mock
    return unittest.mock.patch.dict(os.environ, env, clear=False)
