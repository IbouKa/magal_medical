# Application de Gestion des Données Médicales — Grand Magal de Touba
**Région Médicale de Diourbel**

## Description
Application web Flask + SQLite pour la surveillance épidémiologique du Grand Magal de Touba.

---

## Structure de l'application

```
magal_medical/
├── app.py               # Point d'entrée Flask
├── config.py            # Configuration
├── extensions.py        # SQLAlchemy, LoginManager
├── models.py            # Modèles de données + seed
├── run.py               # Script de démarrage
├── requirements.txt     # Dépendances Python
├── routes/
│   ├── public.py        # Statistiques publiques (sans auth)
│   ├── auth.py          # Connexion / Déconnexion
│   ├── admin.py         # Tableau de bord administrateur
│   └── user.py          # Espace responsable EPS
├── templates/
│   ├── base.html        # Template de base (navbar, footer)
│   ├── auth/            # Login, changement mot de passe
│   ├── public/          # Page statistiques publiques
│   ├── admin/           # Dashboard, EPS, Users, Rapports...
│   └── user/            # Dashboard EPS, Saisie, Fiches
├── static/
│   └── css/style.css    # Styles personnalisés (vert Magal)
└── instance/
    └── magal_medical.db # Base de données SQLite (auto-créée)
```

---

## Installation

```bash
cd magal_medical
pip install -r requirements.txt
python run.py
```

---

## Accès

| Page | URL |
|------|-----|
| Statistiques publiques | http://localhost:5000 |
| Connexion | http://localhost:5000/auth/login |
| Dashboard admin | http://localhost:5000/admin/dashboard |
| Espace EPS | http://localhost:5000/user/dashboard |

---

## Comptes par défaut

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | `admin` | `admin2025` |
| Responsable PS KHAIRA (démo) | `ps_khaira` | `khaira2025` |

---

## Rôles et accès

### Public (sans connexion)
- Statistiques globales par période et par district
- Graphiques de morbidité
- MPE (Maladies à Potentiel Épidémique)
- Taux de complétude

### Responsable EPS (poste_sante / centre_sante / hopital)
- Saisie de la fiche journalière pour chaque période (J-2 → J+3)
- 32 affections : cas simples, hospitalisés, évacués, décédés
- Consultation et modification de ses propres fiches
- Vue de son tableau de bord personnel

### Administrateur
- Gestion des EPS (création, modification)
- Gestion des utilisateurs
- Gestion des éditions
- Saisie directe pour tout EPS
- Rapports consolidés (filtres par période et district)
- Suivi de la complétude en temps réel

---

## Structure des données (basée sur la maquette Excel)

### Périodes
`J-2`, `J-1`, `J` (jour J du Magal), `J+1`, `J+2`, `J+3`

### 32 Affections cataloguées
1. Coups et blessures
2. Accidents domestiques
3. Accidents circulation auto
4. Accidents circulation Moto
5. Accident circulation Charrette
6. Accident voie Publique
7. Accidents de travail
8. Autres accidents
9. Affections cardiovasculaires (HTA...)
10. Paludisme confirmé (TDR+)
11. Affections Respiratoires
12. Gastroentérite / Intoxication
13. Affection appareil digestif
14. Affection buco dentaires
15. Affections ORL
16. Affections de l'oeil et annexes
17. Gynéco obstétrique
18. Affections uro-génitales
19. Affection dermatologiques
20. Affections ostéo articulaires
21. Maladies chroniques (diabète...)
22. Affections neuropsychiatriques
23. Syndrome infectieux
24. Coups de chaleur
25. Atteintes neuromusculaires
26. Autres affections à préciser
27-32. MPE : Rougeole, Méningite, PFA, Choléra, COVID-19 suspects/confirmés

### Zones / Districts
- HOPITAL NDAMATOU
- DISTRICT BAMBEY
- DISTRICT DIOURBEL
- HR DIOURBEL
- DISTRICT MBACKE
- HOP MATLABOUL FAWZAINY
- DISTRICT DAROU MOUSTY
- DISTRICT TOUBA (46 EPS)
- HOPITAL CH KHADIM
- DISTRICT GOSSAS

---

## Technologies
- **Backend** : Python 3.x, Flask 3.0, Flask-SQLAlchemy,