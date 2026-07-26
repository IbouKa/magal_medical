import subprocess
import sys

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True,
                       cwd='c:/Users/ibouk/magal-app/magal_medical')
    print(f"CMD: {cmd}")
    if r.stdout: print("OUT:", r.stdout.strip())
    if r.stderr: print("ERR:", r.stderr.strip())
    print(f"RC: {r.returncode}\n")
    return r.returncode

print("=== Git Fix Script ===\n")

# Show current state
run("git log --oneline --all -6")
run("git status")

# Get remote version of nixpacks.toml
r = subprocess.run('git show origin/master:nixpacks.toml', 
                   capture_output=True, text=True, shell=True,
                   cwd='c:/Users/ibouk/magal-app/magal_medical')
print("=== Remote nixpacks.toml ===")
print(r.stdout or r.stderr)

# Try rebase
rc = run("git rebase origin/master")
if rc != 0:
    print("Rebase conflict - aborting and using merge strategy")
    run("git rebase --abort")
    # Use ours strategy
    rc2 = run("git merge -X ours origin/master")
    if rc2 != 0:
        print("Merge failed - trying force push")
        run("git push -f origin master")
    else:
        run("git push origin master")
else:
    run("git push origin master")

run("git log --oneline --all -5")