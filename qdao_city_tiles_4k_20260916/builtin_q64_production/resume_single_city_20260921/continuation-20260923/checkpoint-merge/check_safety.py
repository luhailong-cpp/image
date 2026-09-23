"""Isolated JSON fixtures only. Does not open/write the five real checkpoint files."""
import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checkpoint", BASE / "merge_checkpoint.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TEST = BASE / ("safety-check-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
TEST.mkdir()
results = []


def fixture(name):
    tx = TEST / name
    tx.mkdir()
    m.TARGETS = {k: tx / "targets" / (k + ".json") for k in m.ORDER}
    entries = []
    for k, p in m.TARGETS.items():
        before, after = m.encode({"key": k, "value": "before"}), m.encode({"key": k, "value": "after"})
        m.write_new(p, before)
        m.write_new(tx / "before" / (k + ".json"), before)
        m.write_new(tx / "after" / (k + ".json"), after)
        entries.append({"key": k, "target": m.relative(p), "beforeSha256": m.digest(before), "afterSha256": m.digest(after)})
    dep = tx / "dependency.json"
    m.write_new(dep, m.encode({"exact": "evidence"}))
    plan = {"applyOrder": m.ORDER, "files": entries,
            "dependencies": [{"file": m.relative(dep), "sha256": m.digest(dep.read_bytes())}],
            "scriptSha256": m.digest((BASE / "merge_checkpoint.py").read_bytes())}
    raw = m.encode(plan)
    m.write_new(tx / "plan.json", raw)
    return tx, m.digest(raw), plan


# Windows deny-sharing is checked independently of the transaction's CAS code.
lock_file = TEST / "exclusive.json"
m.write_new(lock_file, b"before")
lock = m.WinLockedFile(lock_file, True)
try:
    try:
        other = m.WinLockedFile(lock_file, False)
    except OSError as exc:
        assert exc.winerror == 32, exc
    else:
        other.close()
        raise AssertionError("Second handle was not excluded")
    lock.write(b"after")
    assert lock.read() == b"after"
finally:
    lock.close()
results.append("exclusive handle rejects second open; locked write/read verified")

tx, sha, plan = fixture("success")
m.apply(tx, sha)
assert all(m.digest(m.TARGETS[x["key"]].read_bytes()) == x["afterSha256"] for x in plan["files"])
assert m.decode((tx / "apply-receipt.json").read_bytes())["status"] == "complete_all_five_writes_verified"
results.append("five-target success with valid SHA chain and receipt")

tx, sha, plan = fixture("cas-conflict")
m.TARGETS["catalog"].write_bytes(b'{"concurrent":"writer"}')
before_attempt = {k: p.read_bytes() for k, p in m.TARGETS.items()}
try:
    m.apply(tx, sha)
except RuntimeError as exc:
    assert "CAS conflict" in str(exc), exc
else:
    raise AssertionError("Expected CAS conflict")
assert before_attempt == {k: p.read_bytes() for k, p in m.TARGETS.items()}
assert m.decode((tx / "apply-receipt.json").read_bytes())["status"] == "aborted_before_first_write"
results.append("one changed target aborts all writes and preserves concurrent content")

tx, sha, plan = fixture("partial-failure")
real_write = m.WinLockedFile.write


def fail_batch(self, raw):
    if m.decode(raw)["key"] == "batch":
        raise IOError("injected write failure")
    return real_write(self, raw)


m.WinLockedFile.write = fail_batch
try:
    try:
        m.apply(tx, sha)
    except IOError as exc:
        assert "injected" in str(exc), exc
    else:
        raise AssertionError("Expected injected failure")
finally:
    m.WinLockedFile.write = real_write
receipt = m.decode((tx / "apply-receipt.json").read_bytes())
assert receipt["status"] == "partial_commit_manual_recovery_required"
assert receipt["attempted"] == ["ledger", "session", "batch"]
assert receipt["committed"] == ["ledger", "session"]
assert all(m.digest(m.TARGETS[x["key"]].read_bytes()) == x["beforeSha256"] for x in plan["files"] if x["key"] not in receipt["committed"])
results.append("partial failure journal records attempted/committed targets and keeps untouched targets")

summary = {"createdAtUtc": m.now(), "onlyIsolatedJsonFixturesUsed": True,
           "realSharedCheckpointFilesOpenedByTheseTests": False, "passed": len(results), "checks": results}
m.write_new(TEST / "summary.json", m.encode(summary))
print(json.dumps({"testDirectory": str(TEST), **summary}))
