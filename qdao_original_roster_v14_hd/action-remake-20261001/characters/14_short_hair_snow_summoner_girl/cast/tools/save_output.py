import json,sys,hashlib,shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
src=Path(job['source'])
dst=ROOT/job['file']
dst.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,dst)
im=Image.open(dst)
record=json.loads((ROOT/job['request']).read_text(encoding='utf-8-sig'))
record.update(file=job['file'],sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),generatedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),nativeSize=list(im.size),format=im.format,mode=im.mode,toolOutput=job.get('output_hint'),visualStatus=job.get('visualStatus','pending'),actualModel=None,actualQuality=None)
(ROOT/job['record']).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
if job.get('export'):
    out=ROOT/job['export'];out.parent.mkdir(parents=True,exist_ok=True)
    rgba=im.convert('RGBA')
    if min(im.size)<1024 or im.width!=im.height:raise ValueError('native_single_frame_below_1024_or_not_square')
    rgba.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
    derived=dict(file=job['export'],sha256=hashlib.sha256(out.read_bytes()).hexdigest(),width=1024,height=1024,format='PNG',mode='RGBA',derivedFrom=dict(file=job['file'],sha256=record['sha256'],generationRecord=job['record']),operation='uniform_full_canvas_lanczos_downscale_to_1024_no_bbox_crop_no_translation',actualModel=None,actualQuality=None)
    (out.parent/(out.name+'.generation.json')).write_text(json.dumps(derived,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(file=str(dst),sha256=record['sha256'],nativeSize=list(im.size),mode=im.mode,alphaExtrema=im.getchannel('A').getextrema() if 'A' in im.getbands() else None),ensure_ascii=False))

