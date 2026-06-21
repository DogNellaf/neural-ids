@echo off
IF NOT EXIST venv (
    py -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
pause