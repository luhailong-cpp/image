import hashlib, io, json, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
rows=[]
for invname in ('inventory-cast.json','inventory-run-ne-cast.json'):
 for f in load(root/invname)['frames']:
  r=load(root/f['source_record']); receipt=load(root/r['evidence']['receipt'])
  match=re.search(r' as (.+?) by default\.',receipt['output_hint'])
  hp=Path(match.group(1)) if match else None
  np=root/r['file']; fp=root/f['path']; checks={}
  checks['receiptHostMatchesRecord']=hp is not None and hp==Path(r['evidence']['hostOutput'])
  checks['hostExists']=bool(hp and hp.is_file())
  hs=sha(hp) if checks['hostExists'] else None
  ns=sha(np) if np.is_file() else None
  fs=sha(fp) if fp.is_file() else None
  checks['actualHostEqualsActualNative']=hs is not None and hs==ns
  checks['nativeSHAEqualsRecord']=ns==r.get('sha256')==r['export']['derivedFrom']['sha256']
  checks['formalSHAEqualsInventoryAndRecord']=fs==f['sha256']==r['export']['sha256']
  with Image.open(np) as im, Image.open(fp) as formal:
   im.load(); formal.load()
   checks['nativeNativeSizeAndMode']=im.mode=='RGBA' and min(im.size)>=1024 and list(im.size)==f['native_size']
   expected=im.resize((1024,1024),Image.Resampling.LANCZOS)
   checks['formalPixelsFromWholeCanvasLanczos']=formal.mode=='RGBA' and formal.size==(1024,1024) and expected.tobytes()==formal.tobytes()
   buf=io.BytesIO();expected.save(buf,format='PNG')
   expected_sha=hashlib.sha256(buf.getvalue()).hexdigest()
   checks['formalPNGByteForByteRecomputed']=expected_sha==fs
   native_size=list(im.size)
  rows.append({'action':f['action'],'direction':f['direction'],'frame':f['frame'],'inventory':invname,'source_record':f['source_record'],'receipt':r['evidence']['receipt'],'host_path_from_actual_receipt':str(hp),'host_sha256_now':hs,'native_path':r['file'],'native_sha256_now':ns,'native_size':native_size,'formal_path':f['path'],'formal_sha256_now':fs,'independently_recomputed_formal_sha256':expected_sha,'checks':checks,'passed':all(checks.values())})
out={'auditedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'scope':'cast E/W32 + owned run NE9','method':'独立读取每份工具回执output_hint并读取真实host文件，比较host/native实际SHA，再重新全画布LANCZOS导出比较1024像素与PNG字节SHA；非仅核对记录内部自洽。','slots':len(rows),'passed':sum(r['passed'] for r in rows),'failed':[f"{r['action']}/{r['direction']}/{r['frame']:02}" for r in rows if not r['passed']],'duplicateActualNativeSHA':len({r['native_sha256_now'] for r in rows})!=len(rows),'frames':rows}
(root/'records/cast-and-ne-source-audit-20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='frames'},ensure_ascii=False))
