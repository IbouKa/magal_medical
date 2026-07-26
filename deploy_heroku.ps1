# ================================================================
# Script de deploiement Heroku - Application Medicale Magal
# Utilisation: .\deploy_heroku.ps1 -AppName "votre-nom-app"
# ================================================================

param(
    [string]$AppName = "magal-medical-2025"
)

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deploiement Heroku - Magal Medical" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 1. Verifications
Write-Host "`n[1/7] Verification des prerequis..." -ForegroundColor Cyan
$gitOk = git --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Error "Git non trouve"; exit 1 }
Write-Host "  Git OK: $gitOk" -ForegroundColor Gray

$herokuCheck = heroku --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Heroku CLI non installe. Installez depuis: https://devcenter.heroku.com/articles/heroku-cli"
    Write-Host "  Commande: winget install Heroku.HerokuCLI" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Heroku CLI OK" -ForegroundColor Gray

# 2. Login Heroku
Write-Host "`n[2/7] Connexion Heroku..." -ForegroundColor Cyan
heroku auth:whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    heroku login
}
Write-Host "  Connecte" -ForegroundColor Gray

# 3. Git commit
Write-Host "`n[3/7] Commit Git..." -ForegroundColor Cyan
git add .
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Deploy: Application Medicale Grand Magal de Touba"
    Write-Host "  Commit cree" -ForegroundColor Gray
} else {
    Write-Host "  Rien a committer" -ForegroundColor Gray
}

# 4. Creer app Heroku
Write-Host "`n[4/7] Creation application Heroku '$AppName'..." -ForegroundColor Cyan
$existing = heroku apps:info -a $AppName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Application existante detectee" -ForegroundColor Yellow
} else {
    heroku create $AppName
    Write-Host "  Application creee: https://$AppName.herokuapp.com" -ForegroundColor Green
}

# 5. PostgreSQL
Write-Host "`n[5/7] Provision PostgreSQL..." -ForegroundColor Cyan
$addons = heroku addons -a $AppName 2>&1
if ($addons -notmatch "heroku-postgresql") {
    heroku addons:create heroku-postgresql:essential-0 -a $AppName
    Write-Host "  PostgreSQL ajoute (Essential-0 - gratuit 30j)" -ForegroundColor Green
} else {
    Write-Host "  PostgreSQL deja configure" -ForegroundColor Gray
}

# 6. Variables d'environnement
Write-Host "`n[6/7] Configuration des variables..." -ForegroundColor Cyan
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 40 | ForEach-Object {[char]$_})
heroku config:set SECRET_KEY=$secretKey FLASK_DEBUG=False -a $AppName
Write-Host "  SECRET_KEY genere et configure" -ForegroundColor Gray

# 7. Deploy
Write-Host "`n[7/7] Deploiement..." -ForegroundColor Cyan
git push heroku master 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  DEPLOIEMENT REUSSI!" -ForegroundColor Green
    Write-Host "  URL: https://$AppName.herokuapp.com" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    heroku open -a $AppName
} else {
    Write-Error "Deploiement echoue. Verifiez les logs: heroku logs --tail -a $AppName"
}