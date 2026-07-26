# Déploiement Railway — Application Médicale Grand Magal de Touba
## Flask + PostgreSQL sur Railway.app

Railway est plus simple et plus économique que Heroku.
Plan Hobby : 5$/mois — PostgreSQL inclus, 500 heures/mois gratuites.

---

## MÉTHODE 1 : Via Railway CLI (recommandée)

### Étape 1 : Installer Railway CLI

```powershell
# Ouvrir une NOUVELLE fenêtre PowerShell
npm install -g @railway/cli

# Vérifier
railway --version
```

### Étape 2 : Se connecter à Railway

```powershell
Set-Location "c:\Users\ibouk\magal-app\magal_medical"
railway login
# Ouvre le navigateur — se connecter avec GitHub ou Google
```

### Étape 3 : Initialiser le projet Railway

```powershell
railway init
# Saisir un nom : magal-medical-2025
# Sélectionner "Create new project"
```

### Étape 4 : Ajouter PostgreSQL

```powershell
railway add --plugin postgresql
# Railway provisionne automatiquement PostgreSQL
# et injecte DATABASE_URL dans l'environnement
```

### Étape 5 : Configurer les variables d'environnement

```powershell
railway variables set SECRET_KEY="$(python -c "import secrets; print(secrets.token_hex(32))")"
railway variables set FLASK_DEBUG=False
```

### Étape 6 : Déployer

```powershell
railway up
# Railway build et déploie automatiquement
# URL affichée dans le terminal
```

### Étape 7 : Générer un domaine public

```powershell
railway domain
# Ou dans le dashboard : Settings > Networking > Generate Domain
```

---

## MÉTHODE 2 : Via GitHub (plus simple)

### Étape 1 : Pousser sur GitHub

```powershell
Set-Location "c:\Users\ibouk\magal-app\magal_medical"

# Créer un repo sur https://github.com/new
# puis:
git remote add origin https://github.com/VOTRE-USERNAME/magal-medical.git
git branch -M main
git push -u origin main
```

### Étape 2 : Configurer Railway Dashboard

1. Aller sur https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Sélectionner votre repo `magal-medical`
4. Railway détecte automatiquement Python + Procfile

### Étape 3 : Ajouter PostgreSQL dans Railway Dashboard

1. Dans le projet Railway → **New Service** → **Database** → **Add PostgreSQL**
2. Railway injecte automatiquement `DATABASE_URL` dans votre app

### Étape 4 : Variables d'environnement

Dans Railway Dashboard → votre service → **Variables** :
```
SECRET_KEY = une-cle-secrete-tres-longue-aleatoire
FLASK_DEBUG = False
```

### Étape 5 : Déploiement automatique

Railway redéploie automatiquement à chaque `git push`.

---

## Script automatisé Railway CLI

Sauvegarder dans un fichier `deploy_railway.ps1` et exécuter :

```powershell
Set-Location "c:\Users\ibouk\magal-app\magal_medical"

# Login
railway login

# Init projet
railway init

# PostgreSQL
railway add --plugin postgresql

# Variables
$sk = python -c "import secrets; print(secrets.token_hex(32))"
railway variables set SECRET_KEY=$sk FLASK_DEBUG=False

# Deploy
railway up

# Domaine public
railway domain
```

---

## Commandes Railway CLI utiles

```powershell
# Voir les logs en temps réel
railway logs

# Variables d'environnement
railway variables

# Ouvrir dans le navigateur
railway open

# Status du déploiement
railway status

# Console Python interactive
railway run python

# Exécuter une commande dans le contexte Railway
railway run python -c "from app import create_app; app = create_app()"

# Lier à un projet existant
railway link

# Déployer une mise à jour
git add . ; git commit -m "Update" ; railway up
```

---

## Structure des fichiers Railway créés

```
magal_medical/
├── railway.json      # Config Railway (builder, health check)
├── nixpacks.toml     # Build config Nixpacks
├── Procfile          # Commande gunicorn
├── wsgi.py           # Point d'entrée WSGI
├── requirements.txt  # + gunicorn, psycopg2-binary
└── config.py         # Gestion DATABASE_URL (auto PostgreSQL)
```

---

## Architecture Railway

```
Internet (HTTPS automatique)
         |
         v
Railway Router
         |
         v
Gunicorn (wsgi:app, 2 workers)
         |
         v
Flask Application
         |
         v
Railway PostgreSQL (même projet, réseau privé)
```

---

## Variables d'environnement Railway

| Variable | Description | Valeur exemple |
|----------|-------------|----------------|
| `DATABASE_URL` | Auto-injectée par Railway PostgreSQL | `postgresql://user:pwd@host:5432/db` |
| `SECRET_KEY` | Clé de chiffrement Flask | 64 chars aléatoires |
| `FLASK_DEBUG` | Mode debug | `False` |
| `PORT` | Port auto-défini par Railway | Automatique |

---

## Après déploiement

### Accès à l'application
- URL : `https://votre-app.railway.app`
- Stats publiques : `https://votre-app.railway.app/statistiques`
- Login admin : `https://votre-app.railway.app/auth/login`

### Comptes par défaut
| Identifiant | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin2025` | Administrateur |
| `ps_khaira` | `khaira2025` | Responsable PS KHAIRA |

> **Important** : Changer les mots de passe immédiatement après le déploiement !

### Mise à jour du code
```powershell
# Via Railway CLI
git add .
git commit -m "Mise a jour"
railway up

# Via GitHub (si connecté)
git add .
git commit -m "Mise a jour"
git push origin main
# Railway redéploie automatiquement
```

---

## Tarification Railway (Juillet 2026)

| Plan | Prix | RAM | CPU | PostgreSQL |
|------|------|-----|-----|------------|
| Hobby | 5$/mois | 512 MB | 0.5 vCPU | 1 GB inclus |
| Pro | 20$/mois | 8 GB | 8 vCPU | 25 GB |

> Le plan Hobby est largement suffisant pour le Magal.