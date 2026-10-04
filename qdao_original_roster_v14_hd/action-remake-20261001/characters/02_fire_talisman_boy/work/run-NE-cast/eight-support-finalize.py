import json,hashlib,argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
B=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(ZoneInfo('America/New_York')).isoformat()
ap=argparse.ArgumentParser();ap.add_argument('--record',required=True);ap.add_argument('--frame',type=int,required=True);ap.add_argument('--status',required=True);ap.add_argument('--notes',required=True);ap.add_argument('--import-formal',action='store_true');a=ap.parse_args()
if not 1<=a.frame<=16:raise RuntimeError('NE slot bounds')
rp=B/a.record;r=json.loads(rp.read_text(encoding='utf-8-sig'));src=B/r['file'];host=Path(r['evidence']['hostOutput'])
if not src.resolve().is_relative_to(B/'work'/'run-NE-cast'):raise RuntimeError('Native outside NE ownership')
receipt=json.loads((B/r['evidence']['receipt']).read_text(encoding='utf-8-sig'))
if str(host) not in receipt['output_hint']:raise RuntimeError('Receipt does not identify host path')
if sha(src)!=sha(host):raise RuntimeError('HOST/NATIVE MISMATCH')
with Image.open(src) as im:
    im.load()
    if im.mode!='RGBA' or min(im.size)<1024:raise RuntimeError('native mode or dimensions')
    dims=list(im.size);hist=im.getchannel('A').histogram();bbox=im.getchannel('A').getbbox()
    out=im.resize((1024,1024),Image.Resampling.LANCZOS)
r.update({'sha256':sha(src),'width':dims[0],'height':dims[1],'format':'PNG','mode':'RGBA','visualQA':{'status':a.status,'notes':a.notes,'reviewedAt':now()},'technicalQA':{'nativeSingleFrame':True,'size':dims,'transparentPixels':hist[0],'alphaBounds':bbox},'sourceAudit':{'checkedAt':now(),'hostPath':str(host),'hostSHA256':sha(host),'nativeSHA256':sha(src),'matches':True}})
candidate=B/'work/run-NE-cast'/f'{rp.stem}.1024.png';out.save(candidate)
r['candidateExport']={'file':candidate.relative_to(B).as_posix(),'sha256':sha(candidate),'operation':'whole canvas LANCZOS resize only','size':[1024,1024]}
if a.import_formal:
    if a.status!='single_frame_pass_pending_dynamic':raise RuntimeError('Cannot import rejected/unreviewed')
    dst=B/'frames/run/NE'/f'{a.frame:02d}.png';out.save(dst)
    r['export']={'file':dst.relative_to(B).as_posix(),'sha256':sha(dst),'width':1024,'height':1024,'mode':'RGBA','operation':'whole canvas LANCZOS resize only; no bboxfit, translation, mirror or interpolation','derivedFrom':{'file':r['file'],'sha256':sha(src),'native_size':dims}}
    ip=B/'inventory-run-ne-cast.json';inv=json.loads(ip.read_text(encoding='utf-8-sig'))
    entry={'action':'run','direction':'NE','frame':a.frame,'path':dst.relative_to(B).as_posix(),'native_size':dims,'native_evidence':a.record,'source_record':a.record,'sha256':sha(dst),'visual_status':a.status,'client_status':'not_integrated'}
    inv['frames']=[x for x in inv['frames'] if not(x['direction']=='NE' and x['frame']==a.frame)]+[entry];inv['frames'].sort(key=lambda x:(x['direction'],x['frame']))
    inv.update({'target_frames':16,'frame_duration_ms':75,'duration_ms':1200,'ownershipNote':'2026-10-04 root delegated all NE slots; this NE inventory takes precedence over inventory-run-north NE entries after latest imports','updatedAt':now()})
    ip.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'record':a.record,'frame':a.frame,'native':r['file'],'sha256':r['sha256'],'native_size':dims,'status':a.status,'export':r.get('export'),'candidate':r['candidateExport']},ensure_ascii=False))
