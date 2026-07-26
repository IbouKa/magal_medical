# ================================================================
# Commandes a executer dans une NOUVELLE fenetre PowerShell
# Copier-coller ce bloc dans la nouvelle fenetre PowerShell
# ================================================================

Set-Location "c:\Users\ibouk\magal-app\magal_medical"

Write-Host "=== Etape 1: Connexion Heroku ===" -ForegroundColor Cyan
heroku login

Write-Host "=== Etape 2: Creation application Heroku ===" -ForegroundColor Cyan
heroku create magal-medical-2026
# Si le nom est pris, modifier: heroku create magal-medical-diourbel-2026

Write-Host "=== Etape 3: PostgreSQL ===" -ForegroundColor Cyan
heroku addons:create heroku-postgresql:essential-0 -a magal-medical-2026

Write-Host "=== Etape 4: Variables d'environnement ===" -ForegroundColor Cyan
$sk = -join ((65..90)+(97..122)+(48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
heroku config:set SECRET_KEY=$sk FLASK_DEBUG=False -a magal-medical-2026

Write-Host "=== Etape 5: Verification DATABASE_URL ===" -ForegroundColor Cyan
heroku config -a magal-medical-2026

Write-Host "=== Etape 6: Deploiement ===" -ForegroundColor Cyan
git push heroku master

Write-Host "=== Etape 7: Ouverture ===" -ForegroundColor Cyan
heroku open -a magal-medical-2026

Write-Host "=== LOGS en direct ===" -ForegroundColor Green
Write-Host "Pour voir les logs: heroku logs --tail -a magal-medical-2026" -ForegroundColor Yellow