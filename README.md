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
| Base de données | **PostgreSQL** (Railway prod) / SQLite (local dev) |
| Serveur WSGI | Gunicorn 22.0 |
| Frontend | Bootstrap 5.3, Chart.js 4.4 |
| Déploiement | Railway (GitHub intégration, Nixpacks) |

---

## 🚀 Déploiement Railway (GitHub → Auto-deploy)

Le dépôt est connecté à Railway. **Chaque `git push` déclenche un redéploiement automatique.**

### Architecture des services Railway

```
┌──────────────────────┐    Variable Reference       ┌──────────────────────┐
│  Service : app       │ ── DATABASE_URL ───────────▶ │  Service : Postgres  │
│  (Flask / Gunicorn)  │   ${{Postgres.DATABASE_URL}} │  (PostgreSQL 16)     │
└──────────────────────┘    réseau privé Railway      └──────────────────────┘
```

### Variables d'environnement — service app

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | **Référence** vers le service Postgres Railway |
| `SECRET_KEY` | clé aléatoire 64 chars | Clé secrète Flask |
| `FLASK_DEBUG` | `False` | Désactiver le debug en prod |

> ⚠️ `DATABASE_URL` n'est **pas injectée automatiquement** depuis le service Postgres.
> Vous devez l'ajouter manuellement dans le service app via une **Variable Reference**.

### Configurer la Variable Reference DATABASE_URL

1. **Railway Dashboard** → votre projet → cliquer sur le **service application** (pas Postgres)
2. Onglet **Variables** → bouton **New Variable**
3. Remplir :
   - **Name** : `DATABASE_URL`
   - **Value** : `${{Postgres.DATABASE_URL}}`
4. Sauvegarder → Railway redéploie automatiquement

> Le nom entre `${{...}}` doit correspondre exactement au nom affiché sur la tuile du service Postgres dans Railway.

### Générer une SECRET_KEY sécurisée

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Options de connexion PostgreSQL (config.py)

`config.py` configure automatiquement SQLAlchemy pour la production PostgreSQL :

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,   # teste la connexion avant chaque requête
    'pool_recycle': 300,     # recycle les connexions toutes les 5 min
    'pool_size': 5,          # connexions maintenues dans le pool
    'max_overflow': 10,      # connexions supplémentaires si pool plein
}
```

Ces options évitent les erreurs `SSL connection has been closed unexpectedly` ou `connection already closed` fréquentes sur Railway.

### Fichiers de configuration Railway

| Fichier | Rôle |
|---------|------|
| `railway.json` | Builder Nixpacks + health check `/statistiques` + restart policy |
| `nixpacks.toml` | Commande de démarrage Gunicorn |
| `Procfile` | Fallback Heroku-compatible |
| `wsgi.py` | Point d'entrée WSGI pour Gunicorn |
| `runtime.txt` | Version Python (3.12.7) |

### Mettre à jour l'application

```bash
git add .
git commit -m "Description des changements"
git push origin master   # Railway redéploie automatiquement
```

---

## 💻 Développement local

### Prérequis
- Python 3.12+
- pip

### Installation

```bash
git clone https://github.com/IbouKa/magal_medical.git
cd magal_medical

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement locales
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
```

### Lancer l'application

```bash
python run.py
```

Application disponible sur : http://localhost:5000

> En développement, SQLite est utilisé automatiquement (`instance/magal_medical.db`).
> Les tables sont créées automatiquement au premier démarrage via `db.create_all()`.

### Variables locales (`.env`)

```env
SECRET_KEY=dev-secret-key-local
DATABASE_URL=sqlite:///instance/magal_medical.db
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
├── config.py                 # Config DATABASE_URL + engine options PostgreSQL
├── extensions.py             # SQLAlchemy, LoginManager
├── models.py                 # Modèles + seed data (32 affections, 39 EPS)
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
│   ├── base.html             # Layout (navbar, footer, flash messages)
│   ├── auth/                 # login.html, change_password.html
│   ├── public/               # stats.html (graphiques Chart.js)
│   ├── admin/                # dashboard, eps, users, rapports, saisie_directe...
│   └── user/                 # dashboard, saisie, fiches...
│
├── static/
│   ├── css/style.css         # Thème vert Magal
│   ├── js/saisie.js          # Calculs temps réel, soumission AJAX
│   ├── js/offline-saisie.js  # Gestion mode hors-ligne
│   └── sw.js                 # Service Worker (PWA)
│
├── railway.json              # Config Railway (Nixpacks, healthcheck, restart)
├── nixpacks.toml             # Commande démarrage
├── Procfile                  # gunicorn wsgi:app --workers 2 ...
├── runtime.txt               # python-3.12.7
├── requirements.txt          # Dépendances Python
├── .env.example              # Template variables d'environnement
└── instance/                 # SQLite local (ignoré par git)
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