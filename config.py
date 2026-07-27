import os
import re
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)


def get_database_url():
    """
    Gère les DATABASE_URL de Railway, Heroku et locaux.
    - Railway : postgresql://... (utilise DATABASE_URL interne, référence ${{Postgres.DATABASE_URL}})
    - Heroku  : postgres://... (à corriger en postgresql://)
    - Local   : sqlite:///...
    """
    # Railway expose DATABASE_URL (réseau interne) et DATABASE_PUBLIC_URL (externe)
    # On utilise DATABASE_URL pour les connexions internes Railway (plus rapide, sans frais)
    url = os.environ.get('DATABASE_URL')
    if url:
        # Corriger l'ancien préfixe Heroku/Railway postgres:// -> postgresql://
        url = re.sub(r'^postgres://', 'postgresql://', url)
        return url
    # Fallback local SQLite pour développement
    return 'sqlite:///' + os.path.join(INSTANCE_DIR, 'magal_medical.db')


def get_engine_options(db_url):
    """
    Options SQLAlchemy pour PostgreSQL en production (Railway).
    - pool_pre_ping : teste la connexion avant chaque utilisation (évite les connexions mortes)
    - pool_recycle  : recycle les connexions toutes les 5 min (Railway ferme les connexions inactives)
    - pool_size     : nombre de connexions maintenues dans le pool
    - max_overflow  : connexions supplémentaires autorisées si pool plein
    """
    if db_url and db_url.startswith('postgresql://'):
        return {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 5,
            'max_overflow': 10,
        }
    return {}


_db_url = get_database_url()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'magal-medical-secret-key-2025-diourbel')
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options(_db_url)
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    EDITION_COURANTE = 2025
    PERIODES = ['J-2', 'J-1', 'J', 'J+1', 'J+2', 'J+3']
    # Production settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'