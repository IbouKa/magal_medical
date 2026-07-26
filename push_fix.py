import subprocess
cwd = 'c:/Users/ibouk/magal-app/magal_medical'

def run(cmd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
    out = (r.stdout + r.stderr).strip()
    print(f"$ {cmd}")
    if out:
        print(out)
    print()
    return r.returncode

run('git status')
run('git add nixpacks.toml fix_git.bat fix_git2.bat git_fix.py push_fix.py')
run('git commit -m "fix: nixpacks auto-detect Python (removes phases.setup with python312)"')
run('git push origin master')
run('git log --oneline -4')