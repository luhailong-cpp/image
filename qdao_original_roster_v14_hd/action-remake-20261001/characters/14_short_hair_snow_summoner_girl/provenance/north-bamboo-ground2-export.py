import json,hashlib,shutil,sys,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
batch=int(sys.argv[1]);rows=read(R/'provenance'/f'north-bamboo-ground2-batch{batch}-receipts.json')
spec=importlib.util.spec_from_file_location('ef',R/'tools/export_frame.py');ef=importlib.util.module_from_spec(spec);spec.loader.exec_module(ef)
for rc in rows:
 q=rc['q'];src=Path(rc['path']);dest=R/'run/staging'/(q['id']+'.png');shutil.copy2(src,dest);im=Image.open(dest)
 refs=[{'path':p,'sha256':sha(p),'role':['unique native edit target and identity','09 shoe-axis/perspective only','approved painted style'][i]} for i,p in enumerate(q['params']['referenced_image_paths'])]
 native={'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'generatedAt':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'generatedAtEvidence':'host file mtime','recordedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':q['configSnapshot'],'submittedParameters':dict(q['params'],model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host builtin tool did not expose model or quality selectors or returned values','evidence':{'toolReturnedPath':str(src),'outputHint':rc['hint'],'receipt':f'provenance/north-bamboo-ground2-batch{batch}-receipts.json'},'request':f'provenance/{q["id"]}.request.json','references':refs,'editTargetFormal':{'path':q['inputFormalFile'],'sha256':q['inputFormalSha256']},'review':{'status':'pending_visual_review'}}
 save(Path(str(dest)+'.generation.json'),native)
 out=R/'run/staging'/(q['id']+'-registered.png');ef.run(dest,out);meta=read(Path(str(out)+'.generation.json'));pre=sha(out);sr=q['registrationSourceRoot'];s=.8;tx=round(512-s*sr[0]);ty=round(942-s*sr[1])
 im=Image.open(out).convert('RGBA');im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA').save(out)
 meta.update({'sha256':sha(out),'actualModel':None,'actualQuality':None,'registrationTransform':{'method':'one global affine scale; existing native target anatomical root retained after localized AI edit; no per-frame bbox fitting or sole alignment','status':'applied_to_candidate','globalScale':.8,'sourceRoot':sr,'targetRoot':[512,942],'integerTranslation':[tx,ty],'inputSha256':pre,'outputSha256':sha(out),'inputNativeReferenceSha256':q['inputNativeSha256'],'inputRegisteredReferenceSha256':q['inputFormalSha256']},'review':{'status':'pending_visual_review'},'phaseProposal':{'supportLeg':q['supportLeg'],'position':q['position'],'variant':q['variant'],'note':'Proposal only; actual pixels require visual review'}})
 save(Path(str(out)+'.generation.json'),meta)
sheet=Image.new('RGB',(2048,((len(rows)+1)//2)*550),'#667579');dr=ImageDraw.Draw(sheet)
for i,rc in enumerate(rows):
 q=rc['q']
 for k,p in enumerate([Path(q['inputFormalFile']),R/'run/staging'/(q['id']+'-registered.png')]):
  im=Image.open(p).convert('RGBA').resize((512,512));x=(i%2*2+k)*512;y=i//2*550;sheet.paste(im,(x,y+30),im);dr.text((x+8,y+8),q['direction']+q['frame']+(' source' if k==0 else ' P'+str(q['position'])+' candidate'),fill='white')
sheet.save(R/'run/staging'/f'north-bamboo-ground2-batch{batch}-comparison.jpg')
print(f'Saved and registered {len(rows)} candidates; no formal overwritten')
