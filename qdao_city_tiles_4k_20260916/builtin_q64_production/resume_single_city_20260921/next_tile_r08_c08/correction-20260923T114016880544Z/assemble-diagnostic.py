from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import json,hashlib,io
RUN=Path(__file__).resolve().parent;P=RUN.parent;ROOT=P.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
seen={};equiv=[]
def read(p,expected=None,text=False):
 p=Path(p).resolve();b=p.read_bytes();h=sha(b)
 if expected and expected!=h:
  assert text and sha(b.replace(b'\r\n',b'\n'))==expected,('SHA mismatch',str(p),h,expected)
  equiv.append({'file':str(p),'currentSha256':h,'historicalSha256':expected,'operation':'CRLF to LF bytes exactly reconstruct historic SHA'})
 assert p not in seen or seen[p]==h
 seen[p]=h;return b
def info(p):
 p=Path(p).resolve();return {'file':str(p),'sha256':sha(read(p))}
def jread(p,expected=None):return json.loads(read(p,expected,True))
def savej(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return info(p)
def saveim(p,im):
 assert not p.exists();im.save(p);return dict(info(p),pixels=list(im.size))
plan=jread(P/'plan.json');layout=jread(P/'layout-record.json')
assert plan['tile']=='r08_c08' and len(plan['patches'])==16
assert plan['globalCoreLTRB']==[28672,28672,32768,32768]
candidate=Image.new('RGB',(4096,4096));sources=[]
for patch in sorted(plan['patches'],key=lambda x:(x['row'],x['column'])):
 ident=patch['id'];r,c=patch['row'],patch['column'];native=P/patch['outputFile'];b=read(native,patch['nativeSha256'])
 rec=jread(patch['generationRecord']['file'],patch['generationRecord']['sha256'])
 assert rec['sha256']==patch['nativeSha256']==rec['toolOutputSha256']
 assert rec['originalNativeBytesPreserved'] is True and rec['resampled'] is False and rec['finalArtUpscaled'] is False
 im=Image.open(io.BytesIO(b));im.load();assert im.format=='PNG' and im.size==(1254,1254)
 if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
 im=im.convert('RGB');core=im.crop((115,115,1139,1139));candidate.paste(core,(c*1024,r*1024))
 evidence=jread(rec['evidence']['file'],rec['evidence']['sha256'])
 prompt=read(rec['prompt']['file'],rec['prompt']['sha256'],True).decode('utf-8-sig')
 assert prompt==evidence['request']['prompt']
 if rec.get('request'):
  assert jread(rec['request']['file'],rec['request']['sha256'])==evidence['request']
 refs=[]
 for ref in rec['references']:
  f=Path(ref['file']);original=str(f);status='current_bytes_verified'
  if not f.exists() and 'guild-ui-v2' in str(f):f=ROOT/'designs/gameplay-ui/04-guild.png';status='exact_sha_style_alias'
  if not f.exists() and 'next_tile_r08_c09' in str(f):
   matches=[x for x in (P.parent/'next_tile_r08_c09/native').glob('*.png') if sha(x.read_bytes())==ref['sha256']]
   if len(matches)==1:f=matches[0];status='exact_sha_native_relocation'
  if f.exists():read(f,ref['sha256'])
  else:status='historical_reference_absent_not_current_pixel_verification'
  refs.append({'recorded':ref,'resolvedFile':str(f),'status':status})
 sources.append({'id':ident,'row':r,'column':c,'native':info(native),'generationRecord':info(patch['generationRecord']['file']),'toolReceipt':info(rec['evidence']['file']),'sourceCoreLTRB':[115,115,1139,1139],'destinationLTRB':[c*1024,r*1024,(c+1)*1024,(r+1)*1024],'referenceVerification':refs,'actualModel':rec['actualModel'],'actualQuality':rec['actualQuality']})
out=RUN/('diagnostic-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir();qa=out/'qa';qa.mkdir()
candidateinfo=saveim(out/'r08_c08.png',candidate)
for s in sources:
 im=Image.open(s['native']['file']).convert('RGB')
 assert candidate.crop(tuple(s['destinationLTRB'])).tobytes()==im.crop((115,115,1139,1139)).tobytes()
bottompath=Path(layout['bottomCore']['file']);bottom=Image.open(io.BytesIO(read(bottompath,layout['bottomCore']['sha256']))).convert('RGB');assert bottom.size==(4096,4096)
items=[];boards=[]
for axis in ['vertical','horizontal']:
 for k in [1024,2048,3072]:
  segments=[]
  for i in range(4):
   box=(k-192,i*1024,k+192,(i+1)*1024) if axis=='vertical' else (i*1024,k-192,(i+1)*1024,k+192)
   im=candidate.crop(box);ident=f'{axis}-{k}-segment-{i+1}';meta={'id':ident,'kind':'internal_seam','cropLTRB':list(box),'artifact':saveim(qa/(ident+'.png'),im),'passed':None};items.append(meta);segments.append(im)
  board=Image.new('RGB',(768,2048) if axis=='vertical' else (2048,768))
  for i,im in enumerate(segments):board.paste(im,((i%2)*im.width,(i//2)*im.height))
  boards.append({'id':f'{axis}-{k}','kind':'full_internal_seam','coverage':[0,4096],'segmentOrder':'1 2 top, 3 4 bottom, no image resize','artifact':saveim(qa/f'board-{axis}-{k}.png',board),'passed':None})
board=Image.new('RGB',(1152,1152))
for r in range(1,4):
 for c in range(1,4):
  box=(c*1024-192,r*1024-192,c*1024+192,r*1024+192);im=candidate.crop(box);board.paste(im,((c-1)*384,(r-1)*384))
  items.append({'id':f'junction-r{r}-c{c}','kind':'internal_junction','cropLTRB':list(box),'artifact':saveim(qa/f'junction-r{r}-c{c}.png',im),'passed':None})
boards.append({'id':'all-nine-junctions','kind':'internal_junctions','artifact':saveim(qa/'board-nine-junctions.png',board),'passed':None})
board=Image.new('RGB',(2048,768))
for i in range(4):
 im=Image.new('RGB',(1024,384));im.paste(candidate.crop((i*1024,3904,(i+1)*1024,4096)),(0,0));im.paste(bottom.crop((i*1024,0,(i+1)*1024,192)),(0,192));board.paste(im,((i%2)*1024,(i//2)*384))
 items.append({'id':f'bottom-segment-{i+1}','kind':'external_bottom_edge','range':[i*1024,(i+1)*1024],'boundaryY':192,'artifact':saveim(qa/f'bottom-segment-{i+1}.png',im),'passed':None})
boards.append({'id':'bottom-full-edge','kind':'external_bottom_edge','artifact':saveim(qa/'board-bottom.png',board),'passed':None})
preview=saveim(out/'preview-not-acceptance.png',candidate.resize((1024,1024),Image.Resampling.LANCZOS))
qai=savej(qa/'index.json',{'candidate':candidateinfo,'createdAtUtc':now(),'nativeScaleEvidence':True,'halfStripWidth':192,'internalSeams':6,'internalJunctions':9,'bottomNeighbor':info(bottompath),'items':items,'boards':boards,'status':'prepared_not_yet_reviewed','formalAccepted':False,'topLeftRightAndExternalJunctions':'pending'})
assembly=savej(out/'assembly.json',{'schemaVersion':1,'createdAtUtc':now(),'tile':'r08_c08','appearance':'tianyong_festival','purpose':'complete_4k_diagnostic_candidate_known_QA_failures_not_selected_for_production','candidate':candidateinfo,'plan':info(P/'plan.json'),'layout':info(P/'layout-record.json'),'script':info(__file__),'method':'exact native core ownership: sixteen1254x1254 crops [115,115,1139,1139] pasted at step1024; nominal4326 halo envelope cropped to4096 is mathematically identical','upscaled':False,'resampling':False,'blend':False,'registration':False,'guidesUsedAsFinalPixels':False,'allCorePixelsEqualSelectedNativeCores':True,'sources':sources,'lineEndingEquivalence':equiv,'qa':qai,'preview':dict(preview,role='downsampled preview only; excluded from acceptance'),'formalAccepted':False,'runtimeAccepted':False,'knownIssues':['r04_c03 y1024 guide paste band and broken diagonal joint','r04_c04.v3 y1024 guide paste band and broken diagonal joint'],'sourceRetention':'Keep necessary selected native work until repaired final intended game tile and reference links complete. Rejected superseded native PNGs may be removed with textual deletion ledger.'})
for p,h in seen.items():assert p.exists() and sha(p.read_bytes())==h,('CONCURRENT INPUT CHANGE',p)
print(json.dumps({'version':str(out),'candidate':candidateinfo,'assembly':assembly,'qa':qai,'formalAccepted':False}))
