# NeuralIDS

> 🇬🇧 English | [🇷🇺 Русский](README.ru.md)

A desktop application for Windows that captures network traffic in real time, extracts flow features, and classifies them using a neural network (Keras/TensorFlow). Detected attacks are displayed in a graphical interface (PyQt5) and stored in a PostgreSQL database.

## Features

- Real-time network traffic capture via Scapy (`AsyncSniffer`)
- Flow-based feature extraction (80+ features per flow)
- Neural network classification (Keras/TensorFlow) across 15 attack classes
- Graphical interface (PyQt5) with an incident list and a hide/dismiss action
- Attack records stored in PostgreSQL
- CSV export of attack records
- Connection blocking via Windows Firewall (`New-NetFirewallRule`)
- Centralized logging with file rotation

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Traffic capture | Scapy (`AsyncSniffer`), Npcap/WinPcap |
| Machine learning | Keras / TensorFlow, scikit-learn (`StandardScaler`) |
| GUI | PyQt5 |
| Database | PostgreSQL (psycopg2) |
| Logging | Python `logging` with rotation |
| Testing | pytest |

## Requirements

- Python 3.10+
- PostgreSQL 14+
- Windows (traffic capture via Scapy and blocking via Windows Firewall)
- Npcap or WinPcap (for Scapy)

## Installation

```bat
:: 1. Create and activate a virtual environment
py -m venv venv
call venv\Scripts\activate.bat

:: 2. Install dependencies
pip install -r requirements.txt

:: 3. Create the PostgreSQL database
::    psql -U postgres -c "CREATE DATABASE ids;"

:: 4. Configure parameters (or use environment variables — see below)
::    Edit settings.py

:: 5. Run
python main.py
```

Or simply run `run.bat`, which does all of the above automatically.

## Environment Variables

All parameters are read from `settings.py`, but can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `IDS_INTERFACE` | `Беспроводная сеть 2` | Network interface to capture on |
| `IDS_MODEL_NAME` | `model.keras` | Path to the Keras model file |
| `IDS_DEBUG` | `false` | Verbose prediction output |
| `IDS_DB_NAME` | `ids` | PostgreSQL database name |
| `IDS_DB_USER` | `postgres` | Database user |
| `IDS_DB_PASSWORD` | `root` | Database password |
| `IDS_DB_HOST` | `localhost` | Database host |

Example:
```bat
set IDS_INTERFACE=Ethernet
set IDS_DEBUG=true
python main.py
```

## Attack Classes

The neural network classifies traffic into 15 classes (defined in `settings.ATTACKS`):

| Index | Class |
|---|---|
| 0 | Benign |
| 1 | Bot |
| 2 | DoS attacks-SlowHTTPTest |
| 3 | DoS attacks-Hulk |
| 4 | DoS attacks-GoldenEye |
| 5 | Brute Force -Web |
| 6 | Brute Force -XSS |
| 7 | SQL Injection |
| 8 | Infilteration |
| 9–14 | DDoS, FTP/SSH BruteForce |

## Database

On first run, the `attack` table is created automatically. The schema holds 80+ flow features, source/destination IP addresses, attack type, a timestamp, and a visibility flag.

### Useful Functions (db.py)

```python
import db

# Get all visible incidents
attacks = db.get_visible_attacks()

# Hide an incident by id
db.set_hidden(42)

# Export all records to CSV
count = db.export_attacks_csv("attacks_export.csv")

# Attack type statistics
stats = db.get_attack_stats()  # {"Bot": 12, "Benign": 1450, ...}
```

## Running Tests

```bat
pip install pytest
pytest tests/ -v
```

Tests require no network, PostgreSQL, or GPU — all external dependencies are mocked.

## Logging

Logs are printed to the console and saved to `ids.log` (rotated every 5 MB, 3 backups kept).

Levels:
- `INFO` — startup/shutdown, attack detection, database writes
- `WARNING` — attack detected
- `DEBUG` — detailed neural network predictions (enabled via `IDS_DEBUG=true`)
- `ERROR` — database or firewall errors

## Project Structure

```
main.py           — entry point: launches the UI and the IDS in a separate thread
IDS.py            — creates and manages the AsyncSniffer (Scapy)
flow_session.py   — FlowSession: groups packets into flows, triggers prediction
flow.py           — Flow: accumulates features for a single network flow
neural.py         — Keras model loading, data normalization, prediction
db.py             — PostgreSQL CRUD (psycopg2, parameterized queries)
settings.py       — configuration (overridable via environment variables)
logger_config.py  — centralized logging setup

Feature extractors:
  flag_count.py       — TCP flag counting
  flow_bytes.py       — byte / bulk metrics
  packet_count.py     — packet counters by direction
  packet_direction.py — FORWARD / REVERSE enum
  packet_flow_key.py  — flow identification key (src_ip, dst_ip, ports)
  packet_length.py    — packet length stats (min/max/mean/std/var)
  packet_time.py      — timing features (IAT, duration)
  utils.py            — summary statistics (mean/std/min/max/total)

UI/:
  window.py           — main window (incident list)
  incident_item.py    — single incident widget ("Hide" button)

tests/              — pytest test suite (no network, DB, or GPU)
```

## Known Limitations

1. **Data normalization** — the `StandardScaler` in `neural.py` is fit on each batch instead of using the scaler saved during training. For production use, the scaler should be persisted alongside the model (`joblib.dump`) and loaded at startup.
2. **Connection blocking** — requires Windows administrator privileges to call `New-NetFirewallRule`.
3. **Windows only** — Scapy on Windows requires Npcap; blocking via PowerShell is Windows-specific.

## License

[MIT](LICENSE)
