"""Read-only prior-asset audit; outputs only this character's audit/ directory."""
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import hashlib, json, os

ROOT = Path('D:/work/image')
OUT = ROOT / 'qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl/audit'
OLD = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921/14-delivery-preview'
COMBAT = ROOT / 'qdao_original_roster_v14_hd/combat-20260929/characters/14_short_hair_snow_summoner_girl'
RUN = ROOT / 'qdao_original_roster_v14_hd/run-correction-20260930/characters/14_short_hair_snow_summoner_girl'
OUT.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}
entries=[]
for category, base in [('legacy_movement', OLD / 'assets'), ('prior_combat',COMBAT), ('prior_run_correction',RUN)]:
    for p in sorted(base.rglob('*.png')):
        im=Image.open(p)
        recpath=Path(str(p)+'.generation.json') if category=='legacy_movement' else COMBAT/'provenance/receipts'/f'{p.stem}.json'
        rec=load(recpath)
        a=im.getchannel('A') if im.mode=='RGBA' else None
        alpha8=a.point(lambda v:255 if v>8 else 0).getbbox() if a else None
        entry={'category':category,'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaExtrema':list(a.getextrema()) if a else None,'alphaGt8BBox':alpha8,'lowestAlphaGt8Y':alpha8[3]-1 if alpha8 else None,'sourceRecord':recpath.relative_to(ROOT).as_posix() if recpath.exists() else None,'sourceRecordSHA256':sha(recpath) if recpath.exists() else None,'recordedImageShaMatches':rec.get('sha256')==sha(p) if rec else None,'originalNativeSize':rec.get('nativeSize') or [rec.get('width'),rec.get('height')],'sourceArchive':rec.get('sourceArchive'),'originalSourceSHA256':rec.get('derivedFrom',{}).get('sha256'),'configTarget':rec.get('configSnapshot'),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'submittedParameters':rec.get('submittedParameters'),'legacyOperation':rec.get('operation'),'legacyReview':rec.get('visualReview') or rec.get('review'),'countedAsNewProduction':False,'runApprovedByThisAudit':False}
        entries.append(entry)
summary={c:sum(e['category']==c for e in entries) for c in ['legacy_movement','prior_combat','prior_run_correction']}
summary.update({'legacyWalk':128,'legacyIdle':8,'combatCandidateSlots':2,'combatRuntimeFrames':0,'runAcceptedByAudit':0,'targetFrames':196})
doc={'schema_version':1,'character':'14_short_hair_snow_summoner_girl','auditedAtUtc':datetime.now(timezone.utc).isoformat(),'userFacingDate':'2026-10-02 America/New_York','scope':'Existing local committed baseline, read-only; does not include action-remake new production.','summary':summary,'entries':entries}
(OUT/'inventory.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')

def sheet(paths,name,cols=4,cell=300):
    canvas=Image.new('RGB',(cols*cell,((len(paths)+cols-1)//cols)*(cell+26)),(35,43,57))
    draw=ImageDraw.Draw(canvas)
    for i,p in enumerate(paths):
        x=(i%cols)*cell; y=(i//cols)*(cell+26)
        im=Image.open(p).convert('RGBA'); im.thumbnail((cell,cell))
        canvas.paste(im,(x+(cell-im.width)//2,y),im)
        draw.text((x+10,y+cell+5),p.parent.name+'/'+p.stem,fill=(240,240,240))
    canvas.save(OUT/name)
for direction in ['E','W','N','NE','SE','S','SW','NW']:
    sheet(sorted((OLD/'assets/walk'/direction).glob('*.png')),f'walk-{direction}-audit.jpg')
sheet([OLD/'assets/idle/E.png',COMBAT/'staging/hit-E-01-v1.png',COMBAT/'staging/hit-E-03-v4.png',OLD/'assets/idle/W.png'],'combat-audit.jpg',4,400)
print(json.dumps(summary))
