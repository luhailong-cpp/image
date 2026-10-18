import json,hashlib
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def art(p):return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
v=B/'versions/right-r04c14-jade-grout-native-v002';r=read(v/'integration.json')
qa={'tile':'r04_c14','candidate':r['candidate'],'integration':art(v/'integration.json'),'issue':'isolated jadefloor grout dead-end x2020..2180/y3430..3465','status':'production_local_pass','formalAcceptedCount':0,'fullVisualAcceptance':False,'actualNativeCallCount':1,'sourceROI':[255,570,780,635],'editTileXYXY':[1676,3412,2201,3477],'finding':'Thin existing floorjoint now continues from leftstonepost to right coping junction, no floatingdead-end. Jadeframe below y3492 and upper paper/grout are outsideROI and byteunchanged. N/S/E/W clean. Distinct upper16px grout phase underpaper remains unpassed.','allFourPerimetersViewedAt100pct':True,'nativeEventBytesMatch':True,'outsideROIUnchanged':True,'noResizeWarpBlur':True,'actualModel':None}
q=B/'qa/right-r04c14-jade-grout-after-v002.json';save(q,qa)
prev=B/'selections/right-r04c14-candidate-overlay-v018.json';sel=read(prev);sel.update(selectionVersion='right-r04c14-candidate-overlay-v019',candidate=r['candidate'],visualQa=art(q),status='grout_deadend_localpass_remaininguppergrout_andfrontpost',previousOverlaySelection=art(prev));sel['repairIntegrations'].append(art(v/'integration.json'));sel['knownJadeGroutResidual']='Dead-end joint corrected; upper grout~16px phase underpaper remains.'
sp=B/'selections/right-r04c14-candidate-overlay-v019.json';save(sp,sel)
c=read(B/'qa/right-r04c14-resume-checkpoint-v018.json');c.update(currentSelection=art(sp),currentCandidate=r['candidate'],noInFlightImageCall=True);c['subsequentLocalQa'].append(str(q));c['currentWorkingSourceChain'].append('jadegrout525x65nativeROI');c['knownResiduals']=[x for x in c['knownResiduals'] if not x.startswith('original isolated grout')];c['externalMissingNeighbor']='main-city-game-20261009/northeast/r04_c15 absent; do notrestore fromoldGit';save(B/'qa/right-r04c14-resume-checkpoint-v019.json',c)
# Export only crops changed since v015, reuse exact hash matches in v015 or oldv005.
old=read(B/'qa/right-r04c14-current24-v015/index.json');im=Image.open(r['candidate']['file']).convert('RGB');d=B/'qa/right-r04c14-current24-v019';d.mkdir()
rows=[]
for s in old['seams']:
 crop=im.crop(s['crop']);h=hashlib.sha256(crop.tobytes()).hexdigest();same=h==s['pixelSha256'];e=Path(s['evidence'])
 if not same:
  e=d/(s['orientation']+'-'+'-'.join(s['pair'])+'.png')
  with e.open('xb') as f:crop.save(f,format='PNG')
 rows.append({**s,'evidence':str(e),'pixelSha256':h,'unchangedFromV015':same,'unchangedFromV005':s['unchangedFromV005'] and same,'currentStatus':'pending_incremental_assessment','priorEvidence':s['evidence']})
save(d/'index.json',{'candidate':r['candidate'],'formalAcceptedCount':0,'seams':rows})
print(json.dumps({'selection':art(sp),'candidate':r['candidate'],'qa':str(q),'coreCount':16,'formal':0,'v015Unchanged':sum(s['unchangedFromV015'] for s in rows),'v005Unchanged':sum(s['unchangedFromV005'] for s in rows),'index':str(d/'index.json')}))