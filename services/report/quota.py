import json
import os
from datetime import datetime
from core import config

QUOTA_FILE = 'quota.json'

def load_quota():
    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, 'r') as f:
                data = json.load(f)
                # Reset count if the date has changed
                if data.get('date') == str(datetime.now().date()):
                    return data.get('count', 0)
        except (json.JSONDecodeError, ValueError):
            return 0
    return 0

def save_quota(count):
    with open(QUOTA_FILE, 'w') as f:
        json.dump({'date': str(datetime.now().date()), 'count': count}, f)

def check_ocr_limit_reached():
    return load_quota() >= config.OCR_DAILY_LIMIT

def increment_ocr_quota():
    save_quota(load_quota() + 1)