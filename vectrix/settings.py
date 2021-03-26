import os

PRODUCTION_MODE = os.environ.get('PRODUCTION_MODE') == "TRUE"
API_URL = os.environ.get('PLATFORM_URL', None)
