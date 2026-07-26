"""
Script de démarrage - Application Médicale Grand Magal de Touba
"""
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("  Application Médicale Grand Magal de Touba")
    print("  Région Médicale de Diourbel")
    print("="*60)
    print("\n  Accès:")
    print("  -> Statistiques publiques : http://localhost:5000")
    print("  -> Connexion admin        : http://localhost:5000/auth/login")
    print("\n  Comptes par défaut:")
    print("  -> Admin   : admin / admin2025")
    print("  -> EPS demo: ps_khaira / khaira2025")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)