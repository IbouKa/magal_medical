@echo off
cd /d c:\Users\ibouk\magal-app\magal_medical
git fetch origin > git_output.txt 2>&1
git log --oneline --all -6 >> git_output.txt 2>&1
git merge -X ours origin/master -m "merge: keep empty nixpacks.toml" >> git_output.txt 2>&1
git push origin master >> git_output.txt 2>&1
git log --oneline --all -4 >> git_output.txt 2>&1
type git_output.txt
</content