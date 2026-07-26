# ================================================================
# Script de deploiement Railway - Application Medicale Magal
# UTILISATION: Ouvrir une NOUVELLE fenetre PowerShell et executer:
#   Set-Location c:\Users\ibouk\magal-app\magal_medical
#   .\deploy_railway.ps1
# ================================================================

param(
    [string]$ProjectName = "magal-medical-2025"
)

# Recharger PATH pour trouver railway
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Deploiement Railway - Magal Medical" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Verification Railway CLI
try {
    $rv = railway --version 2>&1
    Write-Host "[OK] Railway CLI: $rv" -ForegroundColor Green
} catch {
    Write-Error "Railway CLI non trouve. Installez: npm install -g @railway/cli"
    exit 1
}

# Etape 1: Login
Write-Host ""
Write-Host "[1/6] Connexion a Railway (navigateur va s'ouvrir)..." -ForegroundColor Cyan
railway login
if ($LASTEXITCODE -ne 0) { Write-Error "Connexion echouee"; exit 1 }
Write-Host "[OK] Connecte!" -ForegroundColor Green

# Etape 2: Init projet
Write-Host ""
Write-Host "[2/6] Creation du projet Railway '$ProjectName'..." -ForegroundColor Cyan
Write-Host "Repondre: 'Empty Project', puis nommer: $ProjectName" -ForegroundColor Yellow
railway init
if ($LASTEXITCODE -ne 0) { Write-Error "Init echouee"; exit 1 }

# Etape 3: PostgreSQL
Write-Host ""
Write-Host "[3/6] Ajout de PostgreSQL..." -ForegroundColor Cyan
railway add --plugin postgresql
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Echec ajout PostgreSQL via CLI. Ajouter manuellement dans le dashboard Railway."
    Write-Host "  -> https://railway.app/project > New Service > Database > PostgreSQL" -ForegroundColor Yellow
    Read-Host "Appuyer sur Entree quand PostgreSQL est configure"
}
Write-Host "[OK] PostgreSQL configure!" -ForegroundColor Green

# Etape 4: Variables d'environnement
Write-Host ""
Write-Host "[4/6] Configuration des variables..." -ForegroundColor Cyan
$secretKey = python -c "import secrets; print(secrets.token_hex(40))"
if (-not $secretKey) {
    $secretKey = -join ((65..90)+(97..122)+(48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
}
railway variables set SECRET_KEY="$secretKey" FLASK_DEBUG="False"
Write-Host "[OK] SECRET_KEY et FLASK_DEBUG configures" -ForegroundColor Green

# Verification DATABASE_URL
Write-Host ""
Write-Host "[CHECK] Verification DATABASE_URL..." -ForegroundColor Yellow
railway variables
Write-Host "DATABASE_URL doit etre presente (commence par postgresql://)" -ForegroundColor Yellow
Read-Host "DATABASE_URL est presente? (Appuyer Entree pour continuer)"

# Etape 5: Deploiement
Write-Host ""
Write-Host "[5/6] Deploiement de l'application..." -ForegroundColor Cyan
railway up
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deploiement echoue. Verifier les logs: railway logs"
    exit 1
}
Write-Host "[OK] Deploiement reussi!" -ForegroundColor Green

# Etape 6: Domaine public
Write-Host ""
Write-Host "[6/6] Generation du domaine public..." -ForegroundColor Cyan
railway domain
Write-Host "[OK] Domaine genere!" -ForegroundColor Green

# Afficher les infos
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DEPLOIEMENT RAILWAY TERMINE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Cyan
Write-Host "  railway logs          - Voir les logs" -ForegroundColor Gray
Write-Host "  railway open          - Ouvrir dans le navigateur" -ForegroundColor Gray
Write-Host "  railway status        - Statut du deploy" -ForegroundColor Gray
Write-Host "  railway up            - Redeployer" -ForegroundColor Gray
Write-Host ""
Write-Host "Comptes par defaut:" -ForegroundColor Cyan
Write-Host "  Admin:    admin / admin2025" -ForegroundColor Gray
Write-Host "  Responsable: ps_khaira / khaira2025" -ForegroundColor Gray
Write-Host ""

# Ouvrir dans le navigateur
$open = Read-Host "Ouvrir l'application dans le navigateur? (o/n)"
if ($open -eq "o" -or $open -eq "O") {
    railway open
}