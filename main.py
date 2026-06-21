import logging
import sys
import threading

from PyQt5 import QtWidgets, QtCore

from UI.window import Ui_Form
from UI.incident_item import Ui_item
import db
import IDS
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, TIMER_INTERVAL
from logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        self._step = 0
        self.load_attacks()

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.setInterval(1000)
        self._timer.start()

    def _on_tick(self):
        self._step += 1
        if self._step % TIMER_INTERVAL == 0:
            logger.debug("Обновляю список атак...")
            self.load_attacks()
            self._step = 0

    def load_attacks(self):
        self.ui.incidentList.clear()
        try:
            attacks = db.get_visible_attacks()
        except Exception:
            logger.exception("Не удалось загрузить атаки из БД.")
            return

        for attack in attacks:
            element = Ui_item(attack)
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(WINDOW_WIDTH, 126))
            element.item = item
            element.list = self.ui.incidentList
            self.ui.incidentList.insertItem(self.ui.incidentList.count(), item)
            self.ui.incidentList.setItemWidget(item, element)


def _start_ids_thread():
    """Запускает IDS в отдельном потоке, не блокируя UI."""
    t = threading.Thread(target=IDS.main, daemon=True, name="IDS-Sniffer")
    t.start()
    return t


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()

_start_ids_thread()

sys.exit(app.exec())
