#!/usr/bin/env python3
"""Publish complete accepted V12 characters alongside V11; activate metadata last."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import uuid
from pathlib import Path

from process_roster import APPROVED, sha, write_json
from verify_delivery import verify_character

RESOURCE = Path("Assets/Resources/World/Characters/QdaoRosterV12")
NAMESPACE = uuid.UUID("c00c4dc2-fb2e-5d41-a370-c4b35b4c3a81")


def meta_for(path, project, template):
    meta = Path(str(path) + ".meta")
    if meta.exists():
        return
    guid = uuid.uuid5(NAMESPACE, path.relative_to(project).as_posix()).hex
    value = re.sub(r"(?m)^guid: [0-9a-f]{32}$", f"guid: {guid}", template)
    try:
        with meta.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
    except FileExistsError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--project", type=Path, default=Path("E:/work/mmorpg-client"))
    parser.add_argument("--character", choices=APPROVED, action="append", required=True)
    parser.add_argument("--plan-only", action="store_true", help="Verify complete source and show a plan without changing game files.")
    parser.add_argument("--verify-only", action="store_true", help="Verify already imported files without writes.")
    args = parser.parse_args()
    source, project = args.source.resolve(), args.project.resolve()
    if not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        raise ValueError(f"Not a Unity project: {project}")
    characters = list(dict.fromkeys(args.character))
    plan, approvals = [], {}
    # Finish the entire requested source validation before any client write.
    for character in characters:
        folder = source / character
        result = verify_character(folder, require_visual=True)
        recorded = json.loads((folder / "validation.json").read_text(encoding="utf-8"))
        if recorded.get("status") != "passed" or recorded.get("manifest_sha256") != result["manifest_sha256"] or recorded.get("qc_sha256") != result["qc_sha256"]:
            raise ValueError(f"Run verify_delivery.py after the last visual review: {character}")
        approvals[character] = {"manifest_sha256": result["manifest_sha256"], "qc_sha256": result["qc_sha256"], "validation_sha256": sha(folder / "validation.json")}
        for artifact in result["artifacts"]:
            if artifact["path"].endswith(".png"):
                plan.append({"character": character, "source": f"{character}/{artifact['path']}",
                             "destination": (RESOURCE / character / artifact["path"]).as_posix(), "sha256": artifact["sha256"]})
    if args.plan_only:
        print(json.dumps({"status": "ready", "characters": characters, "png_count": len(plan), "resource_root": str(project / RESOURCE)}, ensure_ascii=False))
        return
    if not args.verify_only:
        template_root = project / "Assets/Resources/World/Characters/QdaoHeadbandBoy"
        texture_template = (template_root / "walk_N.png.meta").read_text(encoding="utf-8")
        folder_template = Path(str(template_root) + ".meta").read_text(encoding="utf-8")
        root = project / RESOURCE
        root.mkdir(parents=True, exist_ok=True)
        meta_for(root, project, folder_template)
        for item in plan:
            dest = project / item["destination"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            for directory in reversed(dest.parents):
                if directory == root or root in directory.parents:
                    meta_for(directory, project, folder_template)
            meta_for(dest, project, texture_template)
            if not dest.exists() or sha(dest) != item["sha256"]:
                shutil.copyfile(source / item["source"], dest)
    for item in plan:
        target = project / item["destination"]
        if not target.is_file() or sha(target) != item["sha256"]:
            raise ValueError(f"Client export mismatch: {target}")
    for character in characters:
        # Runtime reads this only after all the complete character's PNGs match.
        value = {"version": 12, "characterId": character, "frameCount": 8, "frameDurationMs": 60,
                 "dedicatedIdle": True, "contactFrame": 0, "status": "passed", "visualReview": "passed", **approvals[character]}
        metadata = project / RESOURCE / character / "appearance.json"
        if args.verify_only:
            if json.loads(metadata.read_text(encoding="utf-8")) != value:
                raise ValueError(f"Client activation metadata differs: {character}")
        else:
            temporary = metadata.with_suffix(".json.pending")
            write_json(temporary, value)
            temporary.replace(metadata)
            meta_for(metadata, project, "fileFormatVersion: 2\nguid: 00000000000000000000000000000000\nTextScriptImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    if not args.verify_only:
        write_json(project / "Docs/ArtEvidence/qdao-roster-v12-import.json", {"status": "passed", "characters_this_import": characters,
                   "source_root": str(source), "resource_root": RESOURCE.as_posix(), "png_count_this_import": len(plan),
                   "source_approvals": approvals, "files": plan})
    print(json.dumps({"status": "passed", "characters": characters, "png_count": len(plan), "mode": "verified" if args.verify_only else "published"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
