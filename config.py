import os
import re
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)


def get_database_url():
    """
    Heroku fournit DATABASE_URL avec le préfixe 'postgres://'
    SQLAlchemy >= 1.4 nécessite 'postgresql://'
    """
    url = os.environ.get('DATABASE_URL')
    if url:
        # Corriger le préfixe Heroku
        url = re.sub(r'^postgres://', 'postgresql://', url)
        return url
    # Fallback local SQLite
    return 'sqlite:///' + os.path.join(INSTANCE_DIR, 'magal_medical.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'magal-medical-secret-key-2025-diourbel')
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    EDITION_COURANTE = 2025
    PERIODES = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']
    # Production settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'