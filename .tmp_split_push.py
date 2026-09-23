import subprocess, sys, os

REPO = r"D:\luyuan\wuxingqitan\image"
BASE = "bec76875"   # origin/main..main 中唯一已可独立推送的小提交
BATCH = 400 * 1024 * 1024

def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if check and r.returncode != 0:
        print("FAILED:", args, r.stderr.decode("utf-8", "replace")[:2000]); sys.exit(1)
    return r

# 主干上直接回退到 BASE，把其后全部净改动放入暂存区（不建分支、不切换）
git("reset", "-q", "--soft", BASE)

files = [f for f in git("diff", "--cached", "--name-only", "-z").stdout.decode("utf-8").split("\0") if f]
p = subprocess.run(["git", "-C", REPO, "ls-files", "-s", "-z"], capture_output=True)
sha_by_path = {}
for e in p.stdout.decode("utf-8", "replace").split("\0"):
    if not e: continue
    meta, path = e.split("\t", 1)
    sha_by_path[path] = meta.split()[1]
shas = [sha_by_path[f] for f in files if f in sha_by_path]
chk = subprocess.run(["git", "-C", REPO, "cat-file", "--batch-check"],
                     input="\n".join(shas).encode(), capture_output=True)
sz_by_sha = {}
for line in chk.stdout.decode().splitlines():
    parts = line.split()
    if len(parts) >= 3 and parts[1] == "blob":
        sz_by_sha[parts[0]] = int(parts[2])
sized = [(f, sz_by_sha.get(sha_by_path.get(f, ""), 0)) for f in files]
print(f"files={len(files)} total={sum(s for _, s in sized)/1048576:.0f} MiB")

batches, cur, cursz = [], [], 0
for f, s in sorted(sized, key=lambda x: -x[1]):
    if cursz + s > BATCH and cur:
        batches.append(cur); cur, cursz = [], 0
    cur.append(f); cursz += s
if cur: batches.append(cur)
n = len(batches)
print(f"batches={n}")

for i, batch in enumerate(batches, 1):
    git("reset", "-q")
    with open(REPO + r"\.tmp_batch.txt", "wb") as fh:
        fh.write("\0".join(batch).encode("utf-8"))
    git("add", "--pathspec-from-file=.tmp_batch.txt", "--pathspec-file-nul")
    msg = f"人物添加、交接状态更新、删除无用图、清理记录（分批 {i}/{n}）"
    git("commit", "-q", "-m", msg)
    print(f"committed {i}/{n}")
os.remove(REPO + r"\.tmp_batch.txt")

out = git("rev-list", "--reverse", "origin/main..main").stdout.decode().split()
print("PUSH_ORDER " + " ".join(out))
