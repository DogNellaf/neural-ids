import os

# включить режим отладки - дополнительная информация в консоли
IS_DEBUG = os.getenv('IDS_DEBUG', 'false').lower() == 'true'

# название модели
MODEL_NAME = os.getenv('IDS_MODEL_NAME', 'model.keras')

# исключаемые столбцы (не подаются в нейронную сеть)
EXCLUDED_COLUMNS = ['src_ip', 'dst_ip', 'src_port', 'timestamp']

# название интерфейса, с которого перехватываем пакеты
INTERNET_INTERFACE = os.getenv('IDS_INTERFACE', 'Беспроводная сеть 2')

# заголовки атак (список должен соответствовать списку предсказываемых атак нейронной сети, см. train.ipynb)
ATTACKS = [
    'Benign',
    'Bot',
    'DoS attacks-SlowHTTPTest',
    'DoS attacks-Hulk',
    'DoS attacks-GoldenEye',
    'Brute Force -Web',
    'Brute Force -XSS',
    'SQL Injection',
    'Infilteration',
    'DoS attacks-GoldenEye',
    'DoS attacks-Slowloris',
    'FTP-BruteForce',
    'SSH-Bruteforce',
    'DDOS attack-LOIC-UDP',
    'DDOS attack-HOIC',
]

# заголовок отсутствия атаки
NOT_ATTACK = ATTACKS[0]

# параметры сборщика пакетов
GARBAGE_COLLECT_PACKETS = 5
EXPIRED_UPDATE = 240
CLUMP_TIMEOUT = 1
ACTIVE_TIMEOUT = 0.005
BULK_BOUND = 4
FLOW_DURATION = 120
PACKET_DURATION = 5

### параметры интерфейса

# ширина основного окна
WINDOW_WIDTH = 480

# высота основного окна
WINDOW_HEIGHT = 500

### подключение к базе данных

# название базы данных
DATABASE_NAME = os.getenv('IDS_DB_NAME', 'ids')

# пользователь
USERNAME = os.getenv('IDS_DB_USER', 'postgres')

# пароль
PASSWORD = os.getenv('IDS_DB_PASSWORD', 'root')

# сервер
DB_HOST = os.getenv('IDS_DB_HOST', 'localhost')

# название таблицы
TABLE_NAME = 'attack'

# интервал обновления списка атак (сек)
TIMER_INTERVAL = 5