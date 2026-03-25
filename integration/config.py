"""
TASI3 System Configuration
Loads API keys and global settings from environment variables or .env file
"""

import os

# Try to load from .env file using python-dotenv if available
try:
    from dotenv import load_dotenv
    # البحث عن ملف .env في مجلد المشروع الجذر
    _env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(_env_path)
except ImportError:
    pass

SAHMAK_API_KEY = os.environ.get("SAHMAK_API_KEY", "")
SAHMAK_BASE_URL = os.environ.get("SAHMAK_BASE_URL", "https://app.sahmk.sa/api/v1")
