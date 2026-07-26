# Déploiement Heroku — Application Médicale Grand Magal de Touba
## Flask + PostgreSQL

---

## IMPORTANT : Ouvrir une NOUVELLE fenêtre PowerShell
> La fenêtre actuelle exécute le serveur Flask. Toutes les commandes heroku doivent être lancées dans une **nouvelle fenêtre PowerShell**.

---

## Étape 1 : Vérifier l'installation Heroku CLI

Heroku CLI a été installé via winget. Dans une **nouvelle fenêtre PowerShell** :

```powershell
heroku --version
# Résultat attendu: heroku/7.x.x ...
```

Si "heroku non reconnu", fermer et rouvrir PowerShell (pour recharger le PATH).

---

## Étape 2 : Se connecter à Heroku

```powershell
heroku login
# Ouvre le navigateur pour l'authentification
```

---

## Étape 3 : Se placer dans le dossier du projet

```powershell
Set-Location c:\Users\ibouk\magal-app\magal_medical
```

---

## Étape 4 : Créer l'application Heroku

```powershell
# Choisir un nom unique (minuscules, tirets uniquement)
heroku create magal-medical-2025

# OU laisser Heroku générer un nom aléatoire:
heroku create
```

---

## Étape 5 : Ajouter PostgreSQL

```powershell
heroku addons:create heroku-postgresql:essential-0 -a magal-medical-2025
```

> Plans PostgreSQL Heroku:
> - `essential-0` : 5$/mois — 1 GB, 25 connexions
> - `essential-1` : 9$/mois — 10 GB, 25 connexions
> - `basic`       : 9$/mois (ancienne offre)

---

## Étape 6 : Configurer les variables d'environnement

```powershell
# Générer une clé secrète forte
$sk = -join ((65..90)+(97..122)+(48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

heroku config:set `
  SECRET_KEY=$sk `
  FLASK_DEBUG=False `
  -a magal-medical-2025
```

Vérifier:
```powershell
heroku config -a magal-medical-2025
# Doit afficher DATABASE_URL, SECRET_KEY, FLASK_DEBUG
```

---

## Étape 7 : Déployer

```powershell
# Vérifier que vous êtes sur la branche master
git branch
# * master  <-- doit être là

# Déployer
git push heroku master
```

Sortie attendue:
```
remote: -----> Building on the Heroku-22 stack
remote: -----> Detecting buildpack...
remote: -----> Python app detected
remote: -----> Installing python-3.12.7
remote: -----> Installing pip 24.x
remote: -----> Installing requirements with pip
remote: -----> Launching...
remote:        https://magal-medical-2025.herokuapp.com/ deployed to Heroku
```

---

## Étape 8 : Ouvrir l'application

```powershell
heroku open -a magal-medical-2025
```

---

## Commandes utiles après déploiement

```powershell
# Voir les logs en temps réel
heroku logs --tail -a magal-medical-2025

# Accéder à la console Python
heroku run python -a magal-medical-2025

# Voir l'état de l'application
heroku ps -a magal-medical-2025

# Voir les variables d'environnement
heroku config -a magal-medical-2025

# Redémarrer l'application
heroku restart -a magal-medical-2025

# Voir les infos PostgreSQL
heroku pg:info -a magal-medical-2025

# Voir les statistiques DB
heroku pg:diagnose -a magal-medical-2025
```

---

## Mise à jour après modification du code

```powershell
Set-Location c:\Users\ibouk\magal-app\magal_medical
git add .
git commit -m "Mise a jour: description des changements"
git push heroku master
```

---

## Script automatisé (une seule commande)

```powershell
Set-Location c:\Users\ibouk\magal-app\magal_medical
.\deploy_heroku.ps1 -AppName "magal-medical-2025"
```

---

## Architecture de déploiement

```
Internet
   |
   v
Heroku Router (HTTPS)
   |
   v
Gunicorn (wsgi:app) — 2 workers
   |
   v
Flask Application
   |
   v
PostgreSQL (Heroku Postgres Essential-0)
```

---

## Fichiers de déploiement créés

| Fichier | Rôle |
|---------|------|
| `Procfile` | Commande de démarrage gunicorn |
| `wsgi.py` | Point d'entrée WSGI |
| `requirements.txt` | Dépendances (+ gunicorn, psycopg2-binary) |
| `runtime.txt` | Version Python (3.12.7) |
| `config.py` | Gestion DATABASE_URL postgres→postgresql |
| `.gitignore` | Exclusion instance/, .env, __pycache__ |

---

## Comptes par défaut (créés au premier démarrage)

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | `admin` | `admin2025` |
| Responsable PS KHAIRA | `ps_khaira` | `khaira2025` |

> **Changer les mots de passe** après le premier déploiement via `/auth/change-password`