from pathlib import Path
import json,hashlib,shutil,datetime
root=Path(r'E:\work\image\qdao_chibi_roster_v12');site=root/'review/site';oldroot=root.parent/'qdao_chibi_roster_v11'
q=root/'review/browser-qc/review-pages-result.json'
if q.exists():
 report=json.loads(q.read_text());assert report['status']=='failed';shutil.copyfile(q,q.with_name('before-v11-comparison-frames.json'))
records=[]
for cid in ['27_ink_kite_ranger','28_moon_rabbit_artificer']:
 for dr in ['N','NE','E','SE','S','SW','W','NW']:
  for n in range(1,5):
   rel=Path(cid)/'walk'/dr/f'{n:02}.png';src=oldroot/rel;dst=site/'assets/v11'/rel
   assert src.is_file();dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():assert dst.read_bytes()==src.read_bytes()
   else:shutil.copyfile(src,dst)
   digest=hashlib.sha256(src.read_bytes()).hexdigest();assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
   records.append({'path':str(rel),'source':str(src),'sha256':digest})
(site/'v11-comparison-restoration.json').write_text(json.dumps({'status':'passed','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records},indent=2)+'\n',encoding='utf-8')
print('Restored and verified 64 original V11 comparison frames for27/28')
