@echo off
cd /d c:\Users\ibouk\magal-app\magal_medical
echo === Current state ===
git log --oneline --all -5
git status
echo.
echo === Fetching origin ===
git fetch origin
echo.
echo === Remote nixpacks.toml ===
git show origin/master:nixpacks.toml
echo.
echo === Merging with ours strategy ===
git merge -X ours origin/master -m "merge: integrate remote fix, keep empty nixpacks.toml"
echo.
echo === Pushing ===
git push origin master
echo.
echo === Final state ===
git log --oneline --all -5
git status