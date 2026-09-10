"""Check staged UI files against the frozen v10 PNG contracts; never write production assets."""
from pathlib import Path
import argparse
import json
from collections import Counter
from inventory_contracts import PACK, REPO, inspect_png

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", type=Path, default=PACK / "staged")
    parser.add_argument("--output", type=Path, default=PACK / "validation.json")
    args = parser.parse_args()
    staged, output = args.staged.resolve(), args.output.resolve()
    if not staged.is_relative_to(PACK.resolve()) or not output.is_relative_to(PACK.resolve()):
        parser.error("Staging and report paths must stay inside this v10 package")
    baseline = json.loads((PACK / "contracts/current_files.json").read_text(encoding="utf-8"))
    rows = []
    for old in baseline["files"]:
        relative = Path(old["path"])
        candidate = (staged / relative).resolve()
        if not candidate.is_relative_to(staged):
            raise ValueError(f"Unsafe resource path: {relative}")
        row = {"path": old["path"], "family": old["family"], "problems": []}
        if not candidate.is_file():
            row["status"] = "missing"
        else:
            try:
                new = inspect_png(candidate)
                row["actual"] = new
                if new["size"] != old["size"]:
                    row["problems"].append("canvas_changed")
                if new["mode"] != old["mode"]:
                    row["problems"].append("mode_changed")
                if old["alpha_range"] is not None and old["alpha_range"][0] == 0:
                    if new["alpha_range"] is None or new["alpha_range"][0] != 0:
                        row["problems"].append("required_transparency_missing")
                if new["alpha_range"] is not None and new["alpha_range"][1] == 0:
                    row["problems"].append("empty_alpha")
                unchanged = new["pixel_sha256"] == old["pixel_sha256"] and new["mode"] == old["mode"]
                if row["problems"]:
                    row["status"] = "invalid"
                elif unchanged and not old["allowed_unchanged"]:
                    row["status"] = "unchanged_artwork"
                elif unchanged:
                    row["status"] = "allowed_unchanged"
                else:
                    row["status"] = "changed_needs_visual_review"
                row["encoded_bytes_changed"] = new["sha256"] != old["sha256"]
            except Exception as exc:
                row["status"] = "invalid"
                row["problems"].append(str(exc))
        rows.append(row)
    counts = dict(Counter(row["status"] for row in rows))
    ready = all(row["status"] in {"changed_needs_visual_review", "allowed_unchanged"} for row in rows)
    report = {"status": "ready_for_visual_review" if ready else "incomplete",
              "asset_count": len(rows), "counts": counts, "files": rows,
              "limits": "Mechanical checks only. Border/anchor manifests, all visual styles, alpha edges, nine-slice stretch and recomposed screens still require review."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "asset_count", "counts")}))
    return 0 if ready else 1

if __name__ == "__main__":
    raise SystemExit(main())
