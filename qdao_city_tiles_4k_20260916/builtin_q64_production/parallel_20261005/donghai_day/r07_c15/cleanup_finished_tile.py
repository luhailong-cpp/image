"""Audited per-file cleanup confined to this completed tile; no recursive deletion."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
T=Path(__file__).resolve().parent;R=T.parent;D=T/'cleanup';D.mkdir(exist_ok=True)
OUT=T/'output/r07_c15.png';EXT=T/'output/extended-context.png'
OS='4e9e6677f9f456422de5d1acceb359d63bd8908656784f44c30acc20118eff4b';ES='2587e1dc66efda0bb56205f29ab75f5d362070479cd1d25e4034537b1f75aae3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
def norm(s):
 if not isinstance(s,str) or not s.lower().endswith(('.png','.json')):return None
 p=Path(s)
 if not p.is_absolute():p=(R/p)
 return p.resolve()

def plan():
 assert sha(OUT)==OS and sha(EXT)==ES
 neighbor=R/'r07_c16/output/assembly-manifest.json';nm=read(neighbor)
 assert nm['output']['sha256']=='de2ffe83eff08483741521f59e81bbc1ea62927024a86229cb6890eb55477ad0'
 assert sha(Path(nm['output']['file']))==nm['output']['sha256']
 northbind=read(R/'r07_c16/plan.json')['neighbors']['west'];assert Path(northbind['file']).resolve()==OUT.resolve() and northbind['sha256']==OS
 keep={};q=[];seen=set()
 def retain(p,reason):
  p=Path(p).resolve()
  if p.is_relative_to(T) and p.is_file():
   keep.setdefault(str(p),set()).add(reason)
   if p.suffix.lower()=='.json':q.append(p)
   elif p.suffix.lower()=='.png':
    side=Path(str(p)+'.generation.json')
    if side.exists():q.append(side)
    if p.name in ('candidate.png','extended-context.png') and (p.parent/'manifest.json').exists():q.append(p.parent/'manifest.json')
 # Official delivery and its current reproducible source validation.
 for p in [OUT,EXT,T/'output/current-preview.png',T/'output/assembly-manifest.json',T/'plan.json']:
  retain(p,'current official asset, plan or source validation manifest')
 for p in (T/'native').glob('*.png'):retain(p,'current16 native source validated by assembly --validate-only')
 for p in (T/'guides').glob('*.png'):retain(p,'current design/field-of-view guide and native input dependency')
 for p in (T/'qa/assembly').glob('*.png'):retain(p,'current final output QA; unique native-pixel acceptance sheet')
 for p in (T/'qa/assembly-masks').glob('*.png'):retain(p,'current coverage/seam-mask evidence referenced by official assembly')
 # Executable accepted-chain reads not serialized as explicit image paths in its manifest.
 for rel in ['repairs/unified/south-straight/s2/halo-upper-probe.png','repairs/unified/south-straight/s3/affine-final-upper.png','repairs/unified/south-straight/s4-clean-cloth/native-final-upper.png','repairs/unified/south-straight/s4-cloth-edge/cloth-only-eligibility.png']:
  retain(T/rel,'explicit image input of accepted final reconstruction helper')
 # Current unique insertion checks; older duplicate QA will become historical text.
 final=T/'repairs/unified/straight-integrated-v6'
 for p in (final/'qa').glob('*.png'):retain(p,'unique final repaired-boundary/insertion QA still referenced by final review')
 for rel in ['repairs/unified/straight-integrated-v5/qa/left-bridge.png','repairs/unified/straight-integrated-v5/qa/right-bridge.png','repairs/unified/straight-integrated-v5/qa/panel-contour-detail.png']:
  retain(T/rel,'unique final unchanged local-contour QA inherited by accepted review')
 skipped={'qa','insertionQA','actualViews','inheritedActualViews','identicalInheritedViews','unchangedQA','viewedImages','views','actualNativeViews','nativeScopedViews','producerReview','rootIndependentReview','independentReview','previousProducerReview','panelIndependentReview','panelExactPixelProof','panelProof','preview','displayPreview','nativePreview','actualViewSource'}
 def walk(v,key=''):
  if key in skipped:return
  if isinstance(v,dict):
   for k,x in v.items():walk(x,k)
  elif isinstance(v,list):
   for x in v:walk(x,key)
  elif isinstance(v,str):
   p=norm(v)
   if p and p.is_relative_to(T) and p.is_file():
    if '/qa/' in p.as_posix():return
    retain(p,'reachable current source/reference/rebuild dependency')
 while q:
  p=q.pop()
  if p in seen:continue
  seen.add(p)
  try:walk(read(p))
  except (ValueError,UnicodeError):pass
 # Explicitly known script consumers that need these snapshots; keep rather than break their chain.
 for name in ['candidate.png','extended-context.png']:
  for folder in ['refined','straight-integrated','straight-integrated-v4','straight-integrated-v5']:
   retain(T/'repairs/unified'/folder/name,'frozen input directly read by currently accepted reconstruction helpers')
 while q:
  p=q.pop()
  if p in seen:continue
  seen.add(p)
  try:walk(read(p))
  except (ValueError,UnicodeError):pass
 # Final candidate/extended duplicates have canonical replacements and no later reconstruction consumer.
 aliases={}
 for p in (T/'repairs/unified/straight-integrated-v6').glob('*.png'):
  target=OUT if p.name=='candidate.png' else EXT if p.name=='extended-context.png' else None
  if target and sha(p)==sha(target):keep.pop(str(p.resolve()),None);aliases[str(p.resolve())]=ref(target)
 items=[];retained=[]
 for p in sorted(T.rglob('*.png')):
  assert p.resolve().is_relative_to(T) and not p.is_symlink()
  v={**ref(p),'bytes':p.stat().st_size}
  if str(p.resolve()) in keep:
   v['reasons']=sorted(keep[str(p.resolve())]);retained.append(v)
  else:
   v['reason']='superseded/rejected/probe/duplicate intermediate raster; not current delivery or reconstruction input'
   if str(p.resolve()) in aliases:v['canonicalReplacement']=aliases[str(p.resolve())]
   items.append(v)
 result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tileRoot':str(T),'output':ref(OUT),'extended':ref(EXT),'neighborOfficialBinding':ref(neighbor),'neighborPlan':ref(R/'r07_c16/plan.json'),'mode':'planned','currentJsonDependencyRecordsScanned':len(seen),'delete':items,'retain':retained,'deleteCount':len(items),'deleteBytes':sum(v['bytes'] for v in items),'retainCount':len(retained),'retainBytes':sum(v['bytes'] for v in retained),'npzFields':'All numerical registration, alpha and color-difference fields retained; no field deletion.','textRecords':'All model/quality/time/source/hash/provenance text retained. Historical cleanup index supersedes file-availability assumptions without changing generation evidence.','scope':'Only files individually listed under r07_c15; no external writes or recursive directory deletion.'}
 save(D/'cleanup-plan.json',result);print(json.dumps({k:result[k] for k in ['deleteCount','deleteBytes','retainCount','retainBytes','currentJsonDependencyRecordsScanned']}))

def execute():
 p=read(D/'cleanup-plan.json');assert p['tileRoot']==str(T) and sha(OUT)==OS and sha(EXT)==ES
 for v in p['retain']:
  x=Path(v['file']).resolve();assert x.is_relative_to(T) and x.exists() and sha(x)==v['sha256']
 # Complete preflight before the first deletion.
 for v in p['delete']:
  x=Path(v['file']).resolve();assert x.is_relative_to(T) and x.suffix.lower()=='.png' and x.is_file() and not x.is_symlink();assert sha(x)==v['sha256'] and x.stat().st_size==v['bytes']
 for v in p['delete']:Path(v['file']).unlink()
 assert sha(OUT)==OS and sha(EXT)==ES
 p['mode']='executed';p['completedAtUtc']=datetime.now(timezone.utc).isoformat()
 for v in p['delete']:v['availability']='deleted-by-authorized-final-asset-cleanup';v['pixelValidation']='historical-hash-and-text-record-only-not-current-pixels'
 save(D/'cleanup-execution.json',p)
 # An explicit availability registry: old immutable records preserve their historical hashes.
 save(D/'historical-raster-availability.json',{'createdAtUtc':p['completedAtUtc'],'policy':'For every path below, old references are historical text evidence only. The raster is gone, and prior visual review is NOT current pixel validation. CanonicalReplacement is supplied only for byte-identical final duplicates.','entries':p['delete']})
 (D/'README.md').write_text('# r07_c15 清理记录\n\n正式 output 与 extended 已验证且保持原 SHA。清理逐文件执行，未删除目录。\n\n已删除图片的旧 JSON 引用均按 historical-raster-availability.json 解释为历史文字与哈希证据，不能视为当前像素验证。原逐图记录和审核记录未改写。\n\n当前16原生来源、输入风格/视野参考、正式 QA、仍被最终重建链直接读取的冻结图、全部 NPZ 色差/配准/接缝数据仍保留；逐文件理由见 cleanup-execution.json。\n',encoding='utf-8')
 print(json.dumps({'deleted':p['deleteCount'],'bytes':p['deleteBytes'],'retained':p['retainCount']}))
if __name__=='__main__':plan() if len(sys.argv)<2 or sys.argv[1]=='plan' else execute()
