"""Record a locally imported mixed package so later publication protects its GUID/index.

Run only after the formal Unity Editor has imported and rebuilt runtime-index.asset,
then closed. This records file/serialized-index evidence, never creates Unity or
visual acceptance. The pinned historical baseline and prior files stay unchanged.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path

import publish_mixed_roster as pub


def prepare(publication, output):
    publication = pub.approve.child_directory(Path(publication), pub.AUDITS)
    output = pub.approve.child_directory(Path(output), pub.AUDITS)
    pub.require(output.suffix == ".json" and not output.exists(), "Choose a new import inventory JSON")
    receipt = pub.read(publication)
    pub.require(receipt.get("schema") == pub.SCHEMA and
                receipt.get("status") == "published_pending_formal_editor_import" and
                receipt.get("writesPerformed") is True and receipt.get("protectedChangedFiles") == 0 and
                receipt.get("derivedIndexCopied") is False and receipt.get("characterId") in pub.ALLOWED_IDS and
                Path(receipt["project"]).resolve() == pub.FORMAL.resolve(), "A successful current formal publication is required")
    project = pub.exact_project(receipt["project"], pub.FORMAL)
    prefix = pub.CHARACTERS + "/"
    before = {p: row for p, row in receipt["protectedFormal"].items() if p.startswith(prefix)}
    pub.formal_character_baseline(before, receipt["publishedUtc"], receipt.get("previousImportAudits", []))
    after = pub.tree_inventory(project, (pub.CHARACTERS,))
    pub.check_import_extension(before, after, receipt)
    pub.check_local_index(project, receipt)
    pub.require(pub.tree_inventory(project, (pub.CHARACTERS,)) == after, "Formal characters changed during import inventory")
    return {"schema": pub.IMPORT_SCHEMA, "status": "recorded_local_index_inventory", "project": str(project),
            "recordedUtc": datetime.now(timezone.utc).isoformat(), "publicationAudit": str(publication),
            "publicationAuditSha256": pub.sha(publication), "characterResources": after,
            "oldCharacterFilesChanged": 0, "toolSha256": pub.sha(Path(__file__)),
            "scope": "Closed formal project file and local GUID/index bindings only; not Unity test or visual approval"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    result = prepare(args.publication_audit, args.output)
    if args.execute:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(pub.encoded(result))
    print(__import__("json").dumps({k: v for k, v in result.items() if k != "characterResources"}, indent=2))


if __name__ == "__main__":
    main()
