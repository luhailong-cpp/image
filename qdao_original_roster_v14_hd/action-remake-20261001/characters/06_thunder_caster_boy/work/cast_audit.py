import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=[];errors=[];digests=set()
for d in ('E','W'):
 for i in range(16):
  p=ROOT/'runtime'/'cast'/d/f'{i:02d}.png'
  rpath=p.with_name(p.name+'.generation.json')
  r=json.loads(rpath.read_text(encoding='utf-8'))
  im=Image.open(p);im.load()
  source=r['derivedFrom'][0]
  nrpath=ROOT/source['generationRecord'];nr=json.loads(nrpath.read_text(encoding='utf-8'))
  assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
  assert sha(p)==r['sha256']
  assert nr['native']['width']>=1024 and nr['native']['height']>=1024
  assert nr['actualModel'] is None and nr['actualQuality'] is None
  assert nr['submittedParameters']['model'] is None and nr['submittedParameters']['quality'] is None
  prompt=nr['prompt']; assert len(prompt)>300 or '\n' in prompt or (ROOT/prompt).exists()
  assert len(nr['references'])==len(nr['submittedParameters']['referenced_image_paths'])
  assert sha(p) not in digests
  digests.add(sha(p))
  frames.append({'direction':d,'index':i,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generationRecord':rpath.relative_to(ROOT).as_posix(),'nativeSourceRecord':nrpath.relative_to(ROOT).as_posix(),'nativeSize':[nr['native']['width'],nr['native']['height']],'generatedAt':nr['generatedAt'],'holdMs':45,'event':'release' if i==9 else None,'staticSingleFrameReview':'provisional_pass','feetDirectionReview':'contact sheet inspected; no gross opposite or outward turn identified; perspective and sequence still pending','dynamicReview':'not_observed','anchorVerified':False})
audit={'character':'06_thunder_caster_boy','action':'cast','reviewedAt':now,'produced':32,'exported':32,'directions':{'E':16,'W':16},'technicalChecks':'32 unique hashes, full 1024 RGBA alpha, >=1024 native sources, prompt and source records, disclosed model/quality null checked','nativeSizeSet':sorted(set(tuple(f['nativeSize']) for f in frames)),'target':{'model':'gpt-image-2.5-sunburst','quality':'max'},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'timing':{'perFrameMs':45,'totalMs':720,'releaseFrame':9,'releaseStartsMs':405},'anchor':{'root':[512,942],'normalizedUnityPivot':[0.5,0.08],'status':'provisional_unverified','note':'No per-frame bbox/lowest-foot alignment. Full-canvas uniform export only. Actual planted soles and head size still vary; global camera/ground require full animation review.'},'staticReview':{'method':'individual image inspection and 4x4 full-canvas contact sheets; not playback','provisionalSingleFramePassCount':32,'wholeSequenceArtAccepted':False,'correctedFrames':['E01 v2: intermediate wand retraction','W07 v2: wand in front of head, not behind ponytail','W10 v2: small high diagonal followthrough','W12 v2: recovery retracts instead of extending again'],'remaining':['full sequence head/body scale and root continuity','actual planted soles vs virtual floor','15 to idle/00 continuity at normal game size','direction consistency of perspective boots in real playback']},'dynamicReview':{'observed':False,'rawToolError':'Browser is not available: iab','inventory':{'apps':[],'browsers':[]},'methodAttempted':'cua.createBrowserTab iab and cua.getState','continuousVideoEvidence':False},'client':{'integrated':False,'validated':False,'reason':'no local client'},'preview':'../preview/index.html','frames':frames}
foot_fixed={('E',3)}|{('W',i) for i in range(4,13)}
for f in frames:
 f['feetDirectionReview']='individually inspected at full frame; local boot/ankle direction repaired v2; stance preserved; static provisional only' if (f['direction'],f['index']) in foot_fixed else 'individually inspected at full frame; coherent knee/ankle/toe perspective retained; dynamic unverified'
audit['staticReview']['correctedFrames'] += ['E03 v2: near boot now follows east knee/ankle','W04 v2: near boot turned west with knee/ankle','W05 v2: near boot turned west with knee/ankle','W06 v2: near boot turned west with knee/ankle']
audit['staticReview']['correctedFrames'] += ['W07 v3 / W08 v2 / W09 v2 / W10 v4: near boot changed from viewer-facing to west, original head/arms retained','W11/W12 rootaxis_v1: same near boot local rotation; root outputs independently viewed']
audit['staticReview']['feetMethod']='2026-10-04 compared latest 09 cast E/W01 and10. Re-reviewed E/W32 full-canvas contacts and modified W07-12 full-size; discovered six additional front-facing near boots and locally repaired. All current boots follow respective direction. Static axes only, no dynamic claim; see cast_SW_NE_static_audit_20261004.json for SHA-bound review.'
(ROOT/'review'/'cast_audit_20261003.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for d in ('E','W'):
 p=ROOT/'review'/f'cast_{d}_contact_20261003.jpg'
 r={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'createdAt':now,'type':'static_contact_preview','operation':'4x4 full-canvas uniform 384px thumbnails on diagnostic background; not runtime frames','derivedFrom':[{'file':f['file'],'sha256':f['sha256'],'generationRecord':f['generationRecord']} for f in frames if f['direction']==d],'actualModel':None,'actualQuality':None,'modelNote':'deterministic preview of source frames; original generation fields remain in referenced records'}
 p.with_name(p.name+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checked':len(frames),'unique':len(digests),'nativeSizes':audit['nativeSizeSet'],'audit':'review/cast_audit_20261003.json'}))
