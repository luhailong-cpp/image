import sys
sys.dont_write_bytecode=True
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
q=z/'qa'; n=z/'native'; root=Path('D:/work/image')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p): return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rules=[ref(root/'AGENTS.md'),ref(root/'docs/MAP_PARALLEL_SPLIT_20261013.json')]
assert rules[0]['sha256']=='57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'
assert rules[1]['sha256']=='929a52abdb55e6022f83abbe9b48718182bc33fc8a0bc2d50a14f6232dd4e850'
ap=q/'full-tile-r13_c05-assembly.json'; a=read(ap)
assert ref(a['output']['path'])['sha256']=='2afcd0758dee49ae02041523b624b73d94f5c17d0450ebada0ebff3ca72853cb'
issues=[{'id':'rockfoot','center':[1024,1024],'description':'At local x512 near y600-770 the large rock foot and sandy ground meet an abrupt rectangular seam. Restore the continuous rounded rock foot, continuous shadow and naturally consistent sand texture. Retain the exact rock silhouette, tiny pebbles and beach geometry elsewhere.','qa':[1,16,30]}, {'id':'shallow','center':[3072,1024],'description':'At local x512 near y500-750 there is an unnatural olive and ochre rectangular patch in the shallow water. Continue the surrounding pale turquoise and sand-under-water color gradually through the area and retain the same connected white foam and organic caustic shapes. Remove the vertical rectangular color break.','qa':[11,18,32]}, {'id':'wave','center':[3072,2048],'description':'At local x512 near y512-742 there are straight rectangular color boundaries cutting through blue wave cells. Make these few wave cells and their turquoise tone flow continuously and organically, maintaining the existing broad white caustics and water rhythm. Remove the square patch impression without smoothing or blurring texture.','qa':[12,23,35]}]
bad={i for it in issues for i in it['qa']}
viewed=[]
for i,v in enumerate(a['qa']):
 assert ref(v['file'])['sha256']==v['sha256']
 viewed.append({**v,'viewedAtNativeResolution':True,'result':'requires_repair' if i in bad else 'passed'})
write(q/'r13_c05-internal-visual-audit-initial-v1.json',{'tile':'r13_c05','status':'requires_repair','createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','trace':ref(ap),'candidate':a['output'],'context':a['context'],'nativeQaViewedCount':39,'viewed':viewed,'findings':issues,'externalJoins':'pending','formalMapAcceptance':False})
im=Image.open(a['context']['path']).convert('RGB')
jobs=[]
for it in issues:
 cx,cy=it['center']; box=[cx-627,cy-627,cx+627,cy+627]
 stem='r13_c05_'+it['id']+'_repair_v1'; source=q/(stem+'-source.png')
 assert not source.exists(); im.crop(tuple(v+115 for v in box)).save(source)
 prompt='Edit target: the attached exact native map crop. Output exactly 1254 x 1254 pixels, opaque PNG, same framing and pixel scale. This is a local seam correction for the approved daylight Daoist Q-style hand-painted fishing village map. '+it['description']+' Only repair the local center area. Preserve the outer 230 pixels on all four sides, lighting, colors, painterly detail and all unrelated geometry. Keep fine native painted detail; no blur, no redesign, no rescale, no additional objects, no text, grid or UI. The whole output must look like one continuous painting with no rectangular cut boundaries.'
 pp=n/(stem+'.prompt.txt'); assert not pp.exists(); pp.write_text(prompt,encoding='utf-8')
 request={'stem':stem,'tile':'r13_c05','kind':'local_native_repair','createdAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':prompt,'referenced_image_paths':[source.as_posix()],'references':[ref(source)],'sourceContext':a['context'],'tileContextBox':box,'rules':rules,'builtin':True,'actualModel':None,'issue':it}
 rp=n/(stem+'.request.json'); write(rp,request)
 jobs.append({'stem':stem,'request':ref(rp),'source':ref(source),'tileContextBox':box,'repairBounds':[230,230,1024,1024],'margin':100})
write(q/'r13c05-repair-jobs-v1.json',jobs)
print(json.dumps(jobs))
