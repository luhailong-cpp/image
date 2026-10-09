from pathlib import Path
import json,hashlib,datetime,sys
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');t=r/'r11_c15'
sys.path.insert(0,str(r));import production_r11_c15 as pr
pr.p.record('r04_c02',r'C:/Users/luyua/.codex/generated_images/01a11b1a-3c09-7ec2-93da-936056df5cfc/exec-fb4a8496-96b6-41b7-9471-8288a8cafad2.png')
for name in ['r04_c01','r04_c02']:
 p=t/'native'/(name+'.png');record=Path(str(p)+'.generation.json');d=json.loads(record.read_text());d.update(rejected=True,rejectionReason='Invented raised waterline truncates original foreground piles which must remain cropped through bottom edge.',availability='raster deleted; historical source hashes and generation text only',rejectedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 for v in [p,Path(d['evidence']['toolResultSourcePath'])]:
  assert v.is_file() and hashlib.sha256(v.read_bytes()).hexdigest()==d['sha256']
  assert v.resolve().is_relative_to(t.resolve()) or v.resolve().parent==Path(r'C:/Users/luyua/.codex/generated_images/01a11b1a-3c09-7ec2-93da-936056df5cfc').resolve()
  v.unlink()
 (t/'qa'/(name+'-rejected-raised-waterline.generation.json')).write_text(json.dumps(d,indent=2)+'\n')
 record.unlink()
pr.status()

