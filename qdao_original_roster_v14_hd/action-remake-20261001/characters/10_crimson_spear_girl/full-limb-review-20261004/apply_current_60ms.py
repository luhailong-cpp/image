from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,re,subprocess,sys
R=Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
S=R/'full-limb-review-20261004/timing-before-60ms'
S.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
scripts=['tools/build_current_player.py','tools/build_all_directions.py','tools/uniform-player.html','tools/verify_player_timing.cjs','tools/verify_overview_timing.cjs','tools/finalize_delivery.py','tools/verify_delivery_references.py']
files=['delivery-current.json','manifest.json','validation.json','RUN_CONTACT_PLAN.json','animation-timing.json','STATUS.md']+scripts+['preview/index.html','preview/timing-grounding.html','preview/all-directions.html','preview/timing-review-data.json','preview/timing-verification.json','preview/overview-timing-verification.json','preview/reference-verification.json']
files += [p.relative_to(R).as_posix() for p in (R/'runtime/run').rglob('*.generation.json')]
snapshots=[]
for rel in files:
 src=R/rel
 if not src.exists():continue
 dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
 snapshots.append({'file':rel,'beforeSHA256':sha(dst)})
pixels={p.relative_to(R).as_posix():sha(p) for p in (R/'runtime').rglob('*.png')}
if not (S/'runtime-image-hashes.json').exists():write(S/'runtime-image-hashes.json',pixels)
if not (S/'snapshot-index.json').exists():write(S/'snapshot-index.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'purpose':'Current timing text snapshots only; no copied image files','files':snapshots})
d=read(R/'delivery-current.json');d.update(runFrameMs=60,runCycleMs=960)
run_count=0
for group,frames in d['groups'].items():
 if group.startswith('run/'):
  for f in frames:
   f['durationMs']=60;run_count+=1
   meta_path=R/f['generationRecord'];meta=read(meta_path);meta['frameDurationMs']=60;write(meta_path,meta)
assert run_count==128
write(R/'delivery-current.json',d)
m=read(R/'manifest.json');m.update(runFrameMs=60,runCycleMs=960)
m['counts']['run'].update(frameMs=60,cycleMs=960)
for f in m['slots']:
 if f['action']=='run':f['durationMs']=60
write(R/'manifest.json',m)
plan=read(R/'RUN_CONTACT_PLAN.json');plan.update(frameMs=60,cycleMs=960);write(R/'RUN_CONTACT_PLAN.json',plan)
timing=read(R/'animation-timing.json');timing['run'].update(frameMs=60,cycleMs=960);write(R/'animation-timing.json',timing)
for rel in scripts:
 path=R/rel;s=path.read_text(encoding='utf8')
 s=re.sub(r'(?<![\w])75(?![\d])','60',s)
 s=re.sub(r'(?<![\w])1200(?![\d])','960',s)
 s=s.replace('tick(1199)','tick(959)').replace('normal75msAndQuarter300msPerFrame','normal60msAndQuarter240msPerFrame')
 path.write_text(s,encoding='utf8')
p=R/'STATUS.md';s=p.read_text(encoding='utf8').replace('16×75ms=1200ms','16×60ms=960ms');p.write_text(s,encoding='utf8')
v=read(R/'validation.json');v.update(status='pending-full-limb-revision-validation',inventorySHA256=sha(R/'delivery-current.json'),runFrameMs=60,runCycleMs=960,timingVerificationStatus='pending',fullLimbRevisionValidation='pending final art publish; do not infer visual acceptance from timing checks',priorValidationSnapshot='full-limb-review-20261004/timing-before-60ms/validation.json')
write(R/'validation.json',v)
for rel in ['tools/build_current_player.py','tools/build_all_directions.py']:
 subprocess.run([sys.executable,str(R/rel)],check=True)
assert pixels=={p.relative_to(R).as_posix():sha(p) for p in (R/'runtime').rglob('*.png')}
print(json.dumps({'runFrameMs':60,'runCycleMs':960,'runtimeRecordsUpdated':run_count,'previewsRebuilt':3,'runtimePixelsUnchanged':len(pixels),'snapshot':S.as_posix()}))

