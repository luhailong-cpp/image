from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,os

root=Path(__file__).resolve().parent
chosen={'E04':'cast-E-04-foot-v3','E06':'cast-E-06-foot-v3','E08':'cast-E-08-foot-v4','E12':'cast-E-12-continuity-v2','E15':'cast-E-15-continuity-v2','W08':'cast-W-08-continuity-v3','E05':'cast-E-05-foot-v2','E07':'cast-E-07-foot-v2'}
notes={'E04':'Wide stance now follows E05; preceding lower spear/arm pose; rear toe corrected to face right without narrowing stance.','E06':'Wide stance and steeper spear form charge progression; rear toe corrected to right.','E08':'Intermediate steeper spear arc and linked arms; rear boot corrected to right, wide lunge retained.','E12':'Medium-width partial recovery, rear foot moves inward moderately, both toe directions forward/right.','E15':'Shoulder-width settling stance retained; both toes forward/right rather than suddenly closing feet.','W08':'Earlier transition keeps upper grip near forehead, before full release; both toes face left.'}
notes.update(E05='Rear shoe toe changed from outward-left to forward-right; original wide charge stance and upper body retained.',E07='Rear shoe toe corrected to forward-right with matching knee/ankle orientation; high charge pose retained.')
selection_path=root/'SELECTED_REPAIRS_20261003.json'
chosen['W15']='cast-W-15-ground-v2'
notes['W15']='Recovery boots lowered through knee/shin extension; full soles settle at adjacent W14/W16 floor level, toes remain west. Native generation also shifts head modestly upward (~30px); full sequence registration/dynamic review remains required.'
out=json.loads(selection_path.read_text(encoding='utf8')).get('entries',[]) if selection_path.exists() else []
for slot,stem in chosen.items():
 stable=root/f'cast-{slot[0]}-{slot[1:]}.png'; staged=root/(stem+'.png'); sr=Path(str(staged)+'.generation.json'); dr=Path(str(stable)+'.generation.json')
 if not staged.exists():
  continue
 with Image.open(staged) as im:
  assert im.mode=='RGBA' and min(im.size)>=1024
 rec=json.loads(sr.read_text(encoding='utf8')); assert rec['sha256']==hashlib.sha256(staged.read_bytes()).hexdigest()
 old=json.loads(dr.read_text(encoding='utf8')); old['review']={'status':'superseded','reason':notes[slot]};old['imageRetention']='replaced after verified replacement; old PNG removed, source text/SHA retained'
 hist=root/'rejected'/f'cast-{slot[0]}-{slot[1:]}-before-continuity-20261003.generation.json'; hist.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf8')
 rec['replacementOf']={'file':stable.name,'sha256':old['sha256'],'record':str(hist.relative_to(root))};rec['file']=stable.name
 rec['review']={'status':'candidate','targetedStaticRepair':'passed', 'observed':notes[slot],'registration':'not_applied','fullSequenceDynamic':'unverified','client':'not_tested'}
 assert staged.resolve().parent==root and stable.resolve().parent==root
 os.replace(staged,stable); dr.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8');sr.unlink()
 out.append({'slot':slot,'file':stable.name,'sha256':rec['sha256'],'sourceVariant':stem,'observed':notes[slot]})
 # Remove unselected local intermediate PNGs only after stable and metadata are verified.
 assert hashlib.sha256(stable.read_bytes()).hexdigest()==rec['sha256']
 for p in root.glob(f'cast-{slot[0]}-{slot[1:]}-*.png'):
  if '-continuity-' not in p.name and '-foot-' not in p.name: continue
  rp=Path(str(p)+'.generation.json')
  if rp.exists():
   h=json.loads(rp.read_text(encoding='utf8')); h['review']={'status':'superseded intermediate','currentSelection':stable.name};h['imageRetention']='PNG removed after current selection verified; textual source retained'
   (root/'rejected'/rp.name).write_text(json.dumps(h,ensure_ascii=False,indent=2),encoding='utf8');rp.unlink()
  assert p.resolve().parent==root;p.unlink()
status=json.loads((root/'STATUS.json').read_text(encoding='utf8'))
entries=[]
for p in sorted(root.glob('cast-?-??.png')):
 im=Image.open(p);r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf8'))
 entries.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),record=p.name+'.generation.json',nativeSize=list(im.size),mode=im.mode,alphaExtrema=list(im.getchannel('A').getextrema()),bboxAlpha=list(im.getchannel('A').getbbox()),review=r.get('review')))
status.update(updatedAt=datetime.now(timezone.utc).isoformat(),entries=entries,presentCandidateCount=len(entries),targetedNativeRepairSlots=list(chosen),fullSequencePassed=False)
status['reviewSummary']=['All32 native slots present, all RGBA >=1024.','W06/W07 spear-tip boundary repairs selected.','E04/E06/E08/E12/E15/W08 native continuity repairs selected; rear toe direction repaired where required, stance width retained.','Entire-direction fixed registration and dynamic playback still need validation. Other frames require individual toe/knee direction audit under latest user feedback; no whole-sequence pass claimed.','No per-frame bbox scaling or minimum-foot snapping used; no client validation.']
(root/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
(root/'SELECTED_REPAIRS_20261003.json').write_text(json.dumps({'updatedAt':status['updatedAt'],'entries':out,'fullSequencePassed':False},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'selected':out,'nativeCount':len(entries)},ensure_ascii=False))
