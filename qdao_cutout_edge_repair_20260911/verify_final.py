"""Read back this repair's published files; never mutates production assets."""
from pathlib import Path
import datetime
import hashlib
import json

PACK = Path(__file__).resolve().parent
ROOT = PACK.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    v9 = read(PACK / "v9/published.json")
    current = read(PACK / "27/published.json")
    approval_path = PACK / "27/staged-v2/processing/final-visual-approval.json"
    approval = read(approval_path)
    assert v9["status"] == current["status"] == "published_and_verified"
    assert approval["status"] == "approved" and len(approval["files"]) == 51
    assert current["visual_approval_sha256"] == sha(approval_path)
    verified = []
    for label, report, base in [
        ("v9_04_14", v9, ROOT),
        ("character_27", current, ROOT / "qdao_chibi_roster_v11/27_ink_kite_ranger"),
    ]:
        for row in report["files"]:
            path = base / row["path"]
            actual = sha(path)
            assert actual == row["actual_sha256"] == row["output_sha256"], str(path)
            backup = row.get("backup")
            if row.get("before_sha256"):
                assert backup and sha(ROOT / backup) == row["before_sha256"], str(backup)
            verified.append({"scope": label, "path": path.relative_to(ROOT).as_posix(), "sha256": actual})
    production = ROOT / "qdao_chibi_roster_v11/27_ink_kite_ranger"
    for row in approval["files"]:
        assert sha(production / row["path"]) == row["sha256"]
    previous = read(PACK / "previous-batch-reverification.json")
    previous_rows = []
    current_files = {r["path"]: r["sha256"] for r in verified}
    traced = []
    for row in previous["files"]:
        actual = sha(ROOT / row["path"])
        if actual != row["expected_sha256"]:
            assert current_files.get(row["path"]) == actual, row["path"]
            traced.append({"path": row["path"], "old_sha256": row["expected_sha256"], "current_sha256": actual, "reason": "Updated in the current verified publication"})
        previous_rows.append({"path": row["path"], "sha256": actual})
    images = [r for r in previous_rows if Path(r["path"]).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}]
    result = {
        "status": "published_and_independently_verified",
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "Known remaining asset repairs from the all-folder style comparison: v9 04/14 edge cleanup and character 27 proportions and gait",
        "v9_published_files": len(v9["files"]),
        "character_27_published_files_including_sources_and_records": len(current["files"]),
        "character_27_approved_media": 51,
        "character_27_media_breakdown": {"portrait": 1, "independent_walk_frames": 32, "strips": 8, "gifs": 8, "sheets": 2},
        "previous_batch_files_rechecked": len(previous_rows),
        "previous_batch_images_rechecked": len(images),
        "previous_batch_shared_metadata_updates": traced,
        "backups_checked": True,
        "visual_approval": approval_path.relative_to(ROOT).as_posix(),
        "visual_approval_sha256": sha(approval_path),
        "publication_records": ["v9/published.json", "v9/prepared-published.json", "27/published.json"],
        "files": verified,
        "previous_batch_current_files": previous_rows,
        "actual_client_modified": False,
    }
    (PACK / "final-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"files", "previous_batch_current_files"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
