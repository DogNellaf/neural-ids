# NeuralIDS

NeuralIDS — десктопное приложение для Windows, которое в реальном времени перехватывает сетевой трафик, извлекает признаки потоков и классифицирует их нейронной сетью (Keras/TensorFlow). Обнаруженные атаки отображаются в графическом интерфейсе (PyQt5) и сохраняются в базу данных PostgreSQL.

---

## Архитектура

```
main.py           — точка входа: запускает UI + IDS в отдельном потоке
IDS.py            — создаёт и управляет AsyncSniffer (Scapy)
flow_session.py   — FlowSession: группирует пакеты в потоки, запускает предсказание
flow.py           — Flow: накапливает признаки одного сетевого потока
neural.py         — загрузка модели Keras, нормализация данных, предсказание
db.py             — CRUD для PostgreSQL (psycopg2, параметризованные запросы)
settings.py       — конфигурация (перекрывается переменными окружения)
logger_config.py  — централизованная настройка логирования

Признаки потока (feature extractors):
  flag_count.py       — подсчёт TCP-флагов
  flow_bytes.py       — байты / bulk-метрики
  packet_count.py     — счётчики пакетов по направлению
  packet_direction.py — enum FORWARD / REVERSE
  packet_flow_key.py  — ключ идентификации потока (src_ip, dst_ip, ports)
  packet_length.py    — длины пакетов (min/max/mean/std/var)
  packet_time.py      — временны́е характеристики (IAT, duration)
  utils.py            — сводная статистика (mean/std/min/max/total)

UI/:
  window.py           — главное окно (список инцидентов)
  incident_item.py    — виджет одного инцидента (кнопка «Скрыть»)

tests/              — тесты pytest (без сети, БД и GPU)
```

---

## Требования

- Python 3.10+
- PostgreSQL 14+
- Windows (для захвата трафика через Scapy и блокировки через Windows Firewall)
- Npcap или WinPcap (для Scapy)

---

## Установка и запуск

```bat
:: 1. Создать и активировать виртуальное окружение
py -m venv venv
call venv\Scripts\activate.bat

:: 2. Установить зависимости
pip install -r requirements.txt

:: 3. Создать БД PostgreSQL
::    psql -U postgres -c "CREATE DATABASE ids;"

:: 4. Настроить параметры (или через переменные окружения — см. ниже)
::    Отредактировать settings.py

:: 5. Запустить
python main.py
```

Либо через `run.bat`, который делает всё автоматически.

---

## Конфигурация

Все параметры читаются из `settings.py`, но могут быть переопределены переменными окружения:

| Переменная окружения  | По умолчанию         | Описание                          |
|-----------------------|----------------------|-----------------------------------|
| `IDS_INTERFACE`       | `Беспроводная сеть 2`| Сетевой интерфейс для захвата     |
| `IDS_MODEL_NAME`      | `model.keras`        | Путь к файлу модели Keras         |
| `IDS_DEBUG`           | `false`              | Подробный вывод предсказаний      |
| `IDS_DB_NAME`         | `ids`                | Имя базы данных PostgreSQL        |
| `IDS_DB_USER`         | `postgres`           | Пользователь БД                   |
| `IDS_DB_PASSWORD`     | `root`               | Пароль БД                         |
| `IDS_DB_HOST`         | `localhost`          | Хост БД                           |

Пример:
```bat
set IDS_INTERFACE=Ethernet
set IDS_DEBUG=true
python main.py
```

---

## Классы атак

Нейросеть классифицирует трафик по 15 классам (определяются в `settings.ATTACKS`):

| Индекс | Класс                    |
|--------|--------------------------|
| 0      | Benign (нормальный)      |
| 1      | Bot                      |
| 2      | DoS attacks-SlowHTTPTest |
| 3      | DoS attacks-Hulk         |
| 4      | DoS attacks-GoldenEye    |
| 5      | Brute Force -Web         |
| 6      | Brute Force -XSS         |
| 7      | SQL Injection             |
| 8      | Infilteration            |
| 9–14   | DDoS, FTP/SSH BruteForce |

---

## База данных

При первом запуске таблица `attack` создаётся автоматически. Схема содержит 80+ признаков потока, IP-адреса источника и назначения, тип атаки, временну́ю метку и флаг видимости.

### Полезные функции (db.py)

```python
import db

# Получить все видимые инциденты
attacks = db.get_visible_attacks()

# Скрыть инцидент по id
db.set_hidden(42)

# Экспортировать все записи в CSV
count = db.export_attacks_csv("attacks_export.csv")

# Статистика по типам атак
stats = db.get_attack_stats()  # {"Bot": 12, "Benign": 1450, ...}
```

---

## Запуск тестов

```bat
pip install pytest
pytest tests/ -v
```

Тесты не требуют сети, PostgreSQL и GPU — все внешние зависимости замокированы.

---

## Логирование

Логи выводятся в консоль и сохраняются в файл `ids.log` (ротация каждые 5 МБ, 3 резервные копии).

Уровни:
- `INFO` — запуск/остановка, обнаружение атак, сохранение в БД
- `WARNING` — обнаруженная атака
- `DEBUG` — детальное предсказание нейросети (включается `IDS_DEBUG=true`)
- `ERROR` — ошибки БД, брандмауэра

---

## Известные ограничения

1. **Нормализация данных** — `StandardScaler` в `neural.py` обучается на каждом батче вместо использования scaler'а, сохранённого при обучении. Для промышленного применения необходимо сохранить scaler вместе с моделью (`joblib.dump`) и загружать его при старте.

2. **Блокировка соединений** — требует прав администратора Windows для вызова `New-NetFirewallRule`.

3. **Только Windows** — Scapy на Windows требует Npcap; блокировка через PowerShell Windows-специфична.
