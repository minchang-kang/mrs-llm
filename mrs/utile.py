import os
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 기준 log 폴더
LOG_DIR = Path(__file__).parent.parent / "log"

def write_log_to_file(log_message: str, file_name: str = 'debug.log'):
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_DIR / file_name, 'a') as f:
        f.write(f"[{timestamp}] {log_message}\n")
