"""Export the selected E/NE independent poses; preserve sources and explicit framing calibration."""
from pathlib import Path
import json,subprocess,sys
from common import GENERATION,DELIVERY,sha,utc_now

variant='review20260928v2'
e=['E01-v2']+[f'E{i:02}-v1' for i in range(2,17)]
e[8:13]=['E09-v4','E10-v3','E11-v3','E12-v3','E13-v5']
ne=['NE01-v3','NE02-v3','NE03-v3','NE04-v2','NE05-v2','NE06-v1','NE07-v2','NE08-v1','NE09-v9','NE10-v4','NE11-v3','NE12-v3','NE13-v5','NE14-v1','NE15-v1','NE16-v1']
cal={
 'E11-v3':(.88*214/221,'E01-v2 fixed-profile face skin connected extent y344..557 (214px); E11-v3 y330..550 (221px). Forehead-to-chin region drift is 3.27%; uniform whole-image reduction .88*214/221. This does not equalize total actor bbox or remove stride knee bob.'),
 'E12-v3':(.88*214/216,'E01-v2 fixed-profile face skin connected extent y344..557 (214px); E12-v3 y326..541 (216px). Uniform whole-image reduction .88*214/216; no limb geometry editing and no total-bbox normalization.'),
 'E13-v5':(.88*214/222,'E01-v2 fixed-profile face skin connected extent y344..557 (214px); E13-v5 y319..540 (222px). Uniform whole-image reduction .88*214/222; total actor height is not a calibration target, so pose compression remains.'),
 'NE03-v3':(.88*137/146,'NE01-v3 visible facial forehead-to-chin connected extent y376..512 (137px); NE03-v3 y348..493 (146px). Uniform whole-image reduction .88*137/146 to correct framing magnification; head width agrees qualitatively, no per-axis warp, no total-body bbox matching.')}
items=[]
for direction,ids in [('E',e),('NE',ne)]:
 for frame,id in list(enumerate(ids,1))+[(None,direction+'-idle-v1')]:
  rel=f'walk/{direction}/{frame:02}.png' if frame else f'idle/{direction}.png'
  out=DELIVERY/'work'/direction/'variants'/variant/'runtime'/rel
  scale,evidence=cal.get(id,(.88,None))
  if not out.exists():
   args=[sys.executable,'-B',str(Path(__file__).with_name('export_frame.py')),'--archive',str(GENERATION/id),'--direction',direction,'--kind','walk' if frame else 'idle','--variant',variant,'--alpha-floor','2','--chroma-profile','none','--cell-scale',str(scale)]
   if frame:args+=['--frame',str(frame)]
   if evidence:args+=['--scale-evidence',evidence]
   subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
  rec=out.parents[3]/'sources'/rel if False else DELIVERY/'work'/direction/'variants'/variant/'sources'/(rel+'.json')
  items.append({'direction':direction,'frame':frame,'kind':'walk' if frame else 'idle','archive':id,'sourceSha256':sha(GENERATION/id/'raw.png'),'output':str(out),'outputSha256':sha(out),'sourceRecord':str(rec),'cellScale':scale,'scaleEvidence':evidence})
manifest={'character':'09_bamboo_archer_girl','createdAt':utc_now(),'variant':variant,'items':items,'walkCount':32,'idleCount':2,'visualStatus':'pending_full_cycle_review','browserPlayback':'not_performed'}
p=DELIVERY/'east-qa/selection-20260928v2.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(p)
