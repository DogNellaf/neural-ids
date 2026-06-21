import logging
import os

import numpy as np
from keras.models import load_model
from pandas import DataFrame
from sklearn.preprocessing import StandardScaler

from settings import MODEL_NAME, EXCLUDED_COLUMNS

logger = logging.getLogger(__name__)

_model = None
_scaler = StandardScaler()


def _get_model():
    global _model
    if _model is None:
        path = os.path.join(os.path.abspath(os.curdir), MODEL_NAME)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл модели не найден: {path}")
        _model = load_model(path)
        logger.info("Модель загружена из '%s'.", path)
    return _model


def _prepare_dataframe(packets: list) -> DataFrame:
    """Копирует пакеты, удаляет исключаемые колонки и возвращает DataFrame."""
    rows = []
    for packet in packets:
        row = {k: v for k, v in packet.items() if k not in EXCLUDED_COLUMNS}
        rows.append(row)
    df = DataFrame(rows)
    # Заполняем пропуски нулями на случай несогласованности признаков
    df = df.fillna(0)
    return df


def predict(packets: list) -> np.ndarray:
    """Предсказывает класс атаки для списка пакетов.

    Args:
        packets: Список словарей с признаками потока.

    Returns:
        Массив вероятностей классов (shape: 1 x num_classes).
    """
    model = _get_model()
    df = _prepare_dataframe(packets)
    # Примечание: fit_transform здесь выполняет нормализацию по текущему батчу.
    # В идеале scaler должен быть сохранён при обучении и загружен здесь.
    scaled = _scaler.fit_transform(df)
    input_df = DataFrame(scaled[:1])
    result = model.predict(input_df, verbose=0)
    return result
