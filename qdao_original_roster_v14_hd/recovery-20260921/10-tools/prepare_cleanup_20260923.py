"""Read-only image checks and an exact deletion manifest for character 10 only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json

REC=Path(__file__).resolve().parents[1]
ROOT=REC.parents[1]
GEN=REC/'10-generation'
OUT=REC/'10-work/cleanup-20260923'
DEFAULT=Path('C:/Users/Administrator/.codex/generated_images')
THREADS={'01a0c4ab-1960-75b0-bc37-6104e343b5e3','01a0c4ab-bcf0-7c62-9a2a-62536ab300c4','01a0c4b1-3bc5-71d0-92ad-0a3d9a0f0968','01a0c4b7-ef5b-76c3-b8fd-213c5b2f605b'}
REJECTED={
    'W01-v1':'Wrong anatomical grip; rejected in review-log.md',
    'W01-v2':'Grip correction did not take effect; rejected in review-log.md',
    'N05-v1':'High passing boot and excessive sole; superseded by N05-v3',
    'N09-v1':'Wrong/unclear contact; superseded by N09-v2',
    'NE01-v1':'Bent spear shaft; superseded by selected NE01-v2',
    'NE09-v1':'Leading leg did not exchange; superseded by NE09-v3',
    'NE09-v2':'Leading leg did not exchange; superseded by NE09-v3',
    'E01-v1':'Wrong southeast-facing rather than E; rejected in visual-review.json',
    'E01-v2':'Near right leg leading, not requested far left contact; observed in task',
    'E01-v3':'Same incorrect leading leg; viewed by root',
    'E01-v4':'Pose guide did not correct leading leg; reported by generating agent',
    'E01-v6':'Same incorrect leading leg after bounded retry; reported by generating agent',
    'E01-v7':'Root 2026-09-23 review: still near right leg leading; equipment/boot drift',
    'NW01-v1':'Excessive sole and back-kick pose; rejected in task',
    'NW01-v2':'Spear tip clipped; superseded by NW01-v3',
    'NW09-v1':'No leading-leg exchange from NW01; rejected in task',
    'SW01-v1':'Left/right grip exchanged; superseded by SW01-v2',
    'SW05-v1':'Spear butt and boots changed; rejected in task',
    'W09-v1':'No leading-leg exchange from W01; rejected in task',
    'W09-v2':'No leading-leg exchange despite changed references; rejected in task',
    'W09-v3':'Repeated wrong contact phase; rejected in task',
    'W09-v4':'Root 2026-09-23 review: near left leg still leads, not far right',
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
targets=[];keep=[];missing=[]
for folder in sorted(GEN.iterdir()):
    if not folder.is_dir() or not (folder/'raw.png').is_file():continue
    raw=folder/'raw.png';meta=read(folder/'raw.png.generation.json');receipt=read(folder/'generation-receipt.json')
    digest=sha(raw);assert digest==meta['sha256']==receipt['rawSHA256'],folder.name
    if folder.name in REJECTED:
        targets.append({'path':str(raw.resolve()),'sha256':digest,'bytes':raw.stat().st_size,'kind':'rejected-or-superseded-raw','reason':REJECTED[folder.name]})
    else:
        keep.append({'path':str(raw.resolve()),'sha256':digest,'bytes':raw.stat().st_size,'reason':'Only native work-in-progress image for this current candidate; not final-approved'})
    original=Path(receipt['original_generated_file']).resolve()
    assert original.parent.parent==DEFAULT.resolve() and original.parent.name in THREADS,original
    if original.is_file():
        assert sha(original)==digest,original
        targets.append({'path':str(original),'sha256':digest,'bytes':original.stat().st_size,'kind':'host-generated-duplicate','reason':'Byte-identical archive raw exists; raw either retained as unique WIP or separately rejected'})
    else:missing.append(str(original))
contact=REC/'10-delivery-preview/revisions/s-first-check/contact'
for image in sorted(contact.glob('*.jpg')):
    targets.append({'path':str(image.resolve()),'sha256':sha(image),'bytes':image.stat().st_size,'kind':'obsolete-partial-contact-sheet','reason':'Old 7-frame partial diagnostic, no full-loop acceptance; PNGs and HTML retained'})
assert len({t['path'].casefold() for t in targets})==len(targets)
value={'createdAt':datetime.now(timezone.utc).isoformat(),'character':'10_crimson_spear_girl',
       'authorization':'User 2026-09-23: delete originals and fallback versions; retain game images/designs. Current AGENTS.md protects sole unexported WIP.',
       'status':'prepared_not_deleted','recursiveDeletion':False,'targets':targets,'retainedNativeWIP':keep,
       'originalsAlreadyAbsent':missing,'protectedOriginalIdentityDesign':str(ROOT/'q_daoist_character_pack_4096/10_crimson_spear_girl_transparent_4096.png'),
       'historicalEvidenceNote':'Original receipts and source/model text are not rewritten. Their old pixel checks remain historical after deletion.'}
OUT.mkdir(parents=True,exist_ok=True)
path=OUT/'plan.json';assert not path.exists(),'Do not overwrite a reviewed cleanup plan'
path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(path),'deleteFiles':len(targets),'deleteBytes':sum(t['bytes'] for t in targets),'retainedNativeWIP':len(keep),'alreadyAbsentDefaults':len(missing)},ensure_ascii=False))
