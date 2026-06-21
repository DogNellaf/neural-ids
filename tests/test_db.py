"""Тесты модуля db с мокированным psycopg2."""
import sys
from unittest.mock import MagicMock, patch, call
from tests.conftest import *  # noqa


class TestDbModule:
    """Тесты для функций db.py с мокированным соединением БД."""

    def setup_method(self):
        # Сбрасываем глобальное состояние модуля db перед каждым тестом
        import importlib
        if "db" in sys.modules:
            del sys.modules["db"]

    def _import_db_with_mock(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        # Таблица уже существует, чтобы не пытаться создавать
        mock_cursor.fetchone.return_value = (1,)

        with patch("psycopg2.connect", return_value=mock_conn):
            import db
            db._conn = mock_conn
            db._cursor = mock_cursor
        return db, mock_conn, mock_cursor

    def test_get_visible_attacks_empty(self):
        db, conn, cursor = self._import_db_with_mock()
        cursor.fetchall.return_value = []
        result = db.get_visible_attacks()
        assert result == []

    def test_get_visible_attacks_returns_list(self):
        from datetime import datetime
        db, conn, cursor = self._import_db_with_mock()
        cursor.fetchall.return_value = [
            (1, "Bot", "1.2.3.4", "5.6.7.8", datetime(2024, 1, 1, 12, 0, 0)),
        ]
        result = db.get_visible_attacks()
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["title"] == "Bot"
        assert result[0]["src_ip"] == "1.2.3.4"

    def test_set_hidden_uses_parameterized_query(self):
        db, conn, cursor = self._import_db_with_mock()
        db.set_hidden(42)
        cursor.execute.assert_called_with(
            f"UPDATE {db.TABLE_NAME} SET is_visible = FALSE WHERE id = %s",
            (42,),
        )
        conn.commit.assert_called()

    def test_save_attack_commits(self):
        db, conn, cursor = self._import_db_with_mock()
        packets = [{"dst_port": 80, "protocol": 6}]
        db.save_attack(packets, "Bot")
        conn.commit.assert_called()

    def test_save_attack_uses_parameterized_query(self):
        db, conn, cursor = self._import_db_with_mock()
        packets = [{"dst_port": 80, "protocol": 6}]
        db.save_attack(packets, "Bot")
        args, kwargs = cursor.execute.call_args
        sql, values = args
        # Проверяем, что используются плейсхолдеры, а не строковая интерполяция значений
        assert "%s" in sql
        assert 80 in values
        assert "Bot" in values

    def test_get_attack_stats(self):
        db, conn, cursor = self._import_db_with_mock()
        cursor.fetchall.return_value = [("Bot", 5), ("Benign", 100)]
        stats = db.get_attack_stats()
        assert stats["Bot"] == 5
        assert stats["Benign"] == 100

    def test_export_attacks_csv(self, tmp_path):
        db, conn, cursor = self._import_db_with_mock()
        cursor.fetchall.return_value = [(1, "Bot")]
        cursor.description = [("id",), ("title",)]
        filepath = str(tmp_path / "out.csv")
        count = db.export_attacks_csv(filepath)
        assert count == 1
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
        assert lines[0].strip() == "id,title"
        assert "Bot" in lines[1]
