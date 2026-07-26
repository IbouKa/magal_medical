# 🏥 Gestion des Données Médicales — Grand Magal de Touba
### Région Médicale de Diourbel · Edition 2025

Application web de surveillance épidémiologique pour le Grand Magal de Touba.  
Développée avec **Python Flask + PostgreSQL**, déployée sur **Railway**.

---

## 🌐 Accès en ligne

| Page | URL |
|------|-----|
| Statistiques publiques | `https://votre-app.railway.app/statistiques` |
| Connexion | `https://votre-app.railway.app/auth/login` |
| Tableau de bord admin | `https://votre-app.railway.app/admin/dashboard` |
| Espace responsable EPS | `https://votre-app.railway.app/user/dashboard` |

---

## 👥 Niveaux d'accès

### 🔓 Public (sans connexion)
- Statistiques globales : consultants, hospitalisés, évacués, décès
- Filtres par période (J-2 → J+3) et par zone/district
- Graphiques d'évolution et de répartition géographique
- Top 10 affections + Maladies à Potentiel Épidémique (MPE)
- Taux de complétude des soumissions en temps réel

### 👨‍⚕️ Responsable EPS — Poste de Santé / Centre de Santé / Hôpital
- Tableau de bord personnel avec statut des 6 périodes
- **Saisie de la fiche journalière** (32 affections × 4 colonnes)
- Calcul automatique des totaux en temps réel
- Consultation et modification des fiches soumises
- Visualisation de la fiche détaillée

### 🔐 Administrateur
- Dashboard global : KPIs, graphiques, complétude par période
- Gestion des EPS (39 structures pré-chargées)
- Gestion des utilisateurs et des droits
- Gestion des éditions (multi-années)
- **Saisie directe** pour tout EPS
- **Rapports consolidés** filtrables par période et district
- Suivi de complétude en temps réel (46 EPS)

---

## 📊 Données de référence (maquette Excel Magal 2025)

### Zones / Districts (10)
| Zone | Type |
|------|------|
| DISTRICT TOUBA | District |
| HOPITAL NDAMATOU | Hôpital |
| HOPITAL CH KHADIM | Hôpital |
| HOP MATLABOUL FAWZAINY | Hôpital |
| HR DIOURBEL | Hôpital Régional |
| DISTRICT BAMBEY | District |
| DISTRICT DIOURBEL | District |
| DISTRICT MBACKE | District |
| DISTRICT DAROU MOUSTY | District |
| DISTRICT GOSSAS | District |

### Périodes de surveillance (6)
`J-2` → `J-1` → **`J`** (Jour du Magal) → `J+1` → `J+2` → `J+3`

### 32 Affections cataloguées
| Catégorie | Affections |
|-----------|-----------|
| Traumatismes | Coups et blessures, Accidents domestiques, Accidents circulation (auto/moto/charrette), Accident voie publique, Accidents de travail, Autres accidents |
| Cardiovasculaire | Affections cardiovasculaires (HTA...) |
| Infectieux | Paludisme confirmé TDR+, Syndrome infectieux |
| Respiratoire | Affections respiratoires |
| Digestif | Gastroentérite/Intoxication, Affection appareil digestif |
| Autres | Bucco-dentaire, ORL, Ophtalmologie, Gynéco-obstétrique, Uro-génital, Dermatologique, Ostéo-articulaire, Neuropsychiatrique, Coups de chaleur, Atteintes neuromusculaires, Maladies chroniques, Autres |
| **MPE** | **Rougeole, Méningite, PFA, Choléra, COVID-19 suspects/confirmés** |

---

## 🛠 Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12, Flask 3.0 |
| ORM | Flask-SQLAlchemy 3.1 |
| Auth | Flask-Login 0.6 |
| Base de données | PostgreSQL (Railway) / SQLite (local) |
| Serveur WSGI | Gunicorn 22.0 |
| Frontend | Bootstrap 5.3, Chart.js 4.4 |
| Déploiement | Railway (GitHub intégration) |

---

## 🚀 Déploiement Railway (GitHub → Auto-deploy)

Le dépôt est connecté à Railway. **Chaque `git push` déclenche un redéploiement automatique.**

### Variables d'environnement requises dans Railway
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Auto-injectée par le service PostgreSQL Railway |
| `SECRET_KEY` | Clé secrète Flask (générer avec `python -c "import secrets; print(secrets.token_hex(40))"`) |
| `FLASK_DEBUG` | `False` en production |

### Mettre à jour l'application
```bash
git add .
git commit -m "Description des changements"
git push origin main   # Railway redéploie automatiquement
```

### Fichiers de configuration Railway
```
railway.json      ← Builder Nixpacks + health check /statistiques
nixpacks.toml     ← Python 3.12 + pip install
Procfile          ← gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT
wsgi.py           ← Point d'entrée WSGI
```

---

## 💻 Développement local

### Prérequis
- Python 3.12+
- pip

### Installation

```bash
git clone <votre-repo>
cd magal_medical
pip install -r requirements.txt
python run.py
```

L'application démarre sur : http://localhost:5000  
Base de données SQLite créée automatiquement dans `instance/magal_medical.db`

### Variables locales (optionnel)
Copier `.env.example` en `.env` :
```
SECRET_KEY=dev-secret-key-local
FLASK_DEBUG=True
```

---

## 🔑 Comptes par défaut

| Identifiant | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin2025` | Administrateur complet |
| `ps_khaira` | `khaira2025` | Responsable PS KHAIRA (démo) |

> ⚠️ **Changer les mots de passe** après le premier déploiement via `/auth/change-password`

---

## 📁 Structure du projet

```
magal_medical/
├── app.py                    # Factory Flask (create_app)
├── config.py                 # Config DATABASE_URL (Railway/SQLite)
├── extensions.py             # SQLAlchemy, LoginManager
├── models.py                 # Modèles + seed data (32 aff, 39 EPS)
├── wsgi.py                   # Point d'entrée Gunicorn
├── run.py                    # Démarrage développement local
│
├── routes/
│   ├── public.py             # Stats publiques (sans auth)
│   ├── auth.py               # Login/Logout/ChangePassword
│   ├── admin.py              # Dashboard, EPS, Users, Rapports
│   └── user.py               # Saisie journalière, Fiches
│
├── templates/
│   ├── base.html             # Layout (navbar, footer, flash)
│   ├── auth/                 # login.html, change_password.html
│   ├── public/               # stats.html (graphiques Chart.js)
│   ├── admin/                # dashboard, eps, users, rapports...
│   └── user/                 # dashboard, saisie, fiches...
│
├── static/css/style.css      # Thème vert Magal
│
├── railway.json              # Config Railway
├── nixpacks.toml             # Build Nixpacks
├── Procfile                  # Commande Gunicorn
├── runtime.txt               # python-3.12.7
├── requirements.txt          # Dépendances Python
└── instance/                 # SQLite (développement local, ignoré git)
```

---

## 📋 Modèle de données

```
Edition (annee, active)
    └── FicheJournaliere (eps, periode, statut, observations)
            └── LigneConsultation (affection, cas_simples, hospitalises, evacues, decedes)

District (nom)
    └── EPS (nom, type: poste_sante|centre_sante|hopital|district)
            └── User (username, role: admin|responsable)

Affection (numero, libelle, categorie, is_mpe)
ServiceDiagnostic (eps, edition, periode, labo, radio, echo, scanner, bloc)
```

---

## 📜 Licence

Usage exclusif — Région Médicale de Diourbel — Grand Magal de Touba 2025