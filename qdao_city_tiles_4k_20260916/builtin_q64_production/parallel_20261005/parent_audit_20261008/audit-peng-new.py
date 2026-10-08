from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,hashlib
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005');A=P/'parent_audit_20261008';D=P/'penglai_day'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
sel=read(D/'asset-index.json');tm=read(D/'tile-manifest.json'); out=[]
for tile in ['r09_c14','r10_c13']:
 e=sel['currentCandidates'][tile]; matching=next(x for x in tm['tiles'] if x['id']==tile)
 assert e['file']==matching['file'] and e['sha256']==matching['sha256']
 p=Path(e['file']);gp=Path(str(p)+'.generation.json');g=read(gp)
 assert sha(p)==e['sha256']==g['sha256'];assert len(g['derivedFrom'])==16
 rebuilt=Image.new('RGB',(4096,4096));sources=[];positions=set()
 for s in g['derivedFrom']:
  n=Path(s['file']);ng=Path(str(n)+'.generation.json');nd=read(ng)
  assert sha(n)==s['sha256']==nd['sha256']
  r,c=int(n.stem[1])-1,int(n.stem[2])-1;positions.add((r,c))
  with Image.open(n) as im:
   assert im.size==(1254,1254);assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
   rebuilt.paste(im.convert('RGB').crop((115,115,1139,1139)),(c*1024,r*1024))
  prompt=Path(nd['prompt']);assert prompt.is_file()
  assert prompt.read_text(encoding='utf-8-sig').strip()==nd['submittedParameters']['prompt'].strip()
  assert nd['route']=='builtin' and nd['tool']=='image_gen.imagegen' and nd['actualModel'] is None and nd['actualQuality'] is None
  refs=[]
  for q in nd['references']:
   exists=Path(q['file']).is_file();same=(sha(q['file'])==q['sha256']) if exists else None
   assert same is not False,(tile,n,q)
   refs.append(dict(**q,existsAtAudit=exists,shaMatchesAtAudit=same))
  host=Path(nd['toolResultPath']);hostsame=sha(host)==sha(n) if host.exists() else None
  assert hostsame is not False
  receipt=Path(nd['evidence']['toolOutputHintFile']);assert receipt.is_file()
  sources.append({'native':ref(n),'generationRecord':ref(ng),'prompt':ref(prompt),'receipt':ref(receipt),'toolOutput':{'path':host.as_posix(),'available':host.is_file(),'matchesNative':hostsame},'references':refs,'nativePixels':[1254,1254],'sourceCoreBoxLTRB':[115,115,1139,1139],'destinationXY':[c*1024,r*1024],'actualModel':None,'actualQuality':None})
 assert positions=={(r,c) for r in range(4) for c in range(4)}
 with Image.open(p) as im:
  assert im.size==(4096,4096);assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
  assert ImageChops.difference(im.convert('RGB'),rebuilt).getbbox() is None
 qa=[];issues=['Seam QA remains pending; no tile, city or client formal acceptance.']
 if tile=='r09_c14':
  q=D/tile/'qa/native-initial/visual-review.json';qr=read(q);qa=[ref(q)]
  issues+=['Owner initial native review explicitly finds straight material/colour changes on internal cuts and west joint; not seamless or final.']
 out.append({'appearance':'penglai_day','tileId':tile,'core':ref(p),'generationRecord':ref(gp),'selectionSource':ref(D/'asset-index.json'),'secondaryRegistry':ref(D/'tile-manifest.json'),'selectedEntry':e,'eligibleCompletePixelCandidate':True,'sourceCount':16,'allNative1254SourcesVerified':True,'nativeCoreReconstructionPixelExact':True,'pixels':[4096,4096],'opaque':True,'sources':sources,'qaEvidence':qa,'qaStatus':e['status'],'remainingLimitations':issues,'formalAccepted':False})
proof={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'two_current_selected_full_pixel_candidates_source_verified_not_seam_accepted','baseParentIndex':ref(A/'verified-current-index.json'),'additions':out,'newCoordinateCount':2,'formalAcceptedCount':0,'childModified':False}
p=A/'penglai-new-coordinate-source-audit.json';p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'file':str(p),'sha256':sha(p),'newCoordinates':[x['tileId'] for x in out]}))
