from pathlib import Path
import json,shutil,hashlib,subprocess
r=Path('E:/work/image/qdao_original_roster_v13/generation/01_ice_sword_girl');items=json.loads((r/'tool-responses.json').read_text(encoding='utf-8-sig'))
for x in items:
 d=r/x['batch'];src=Path(x['generated_source_path']);out=d/'raw.png'
 if not out.exists():shutil.copy2(src,out)
 assert hashlib.sha256(out.read_bytes()).hexdigest()==hashlib.sha256(src.read_bytes()).hexdigest()
 x['raw_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(d/'tool-result.json').write_text(json.dumps(x,indent=2),encoding='utf8')
for batch,mapping in [('S-keys-v3','1,5,9,13'),('S-quarter25-v1','2,6,10,14'),('S-quarter50-v1','3,7,11,15'),('S-quarter75-v1','4,8,12,16')]:
 d=r/batch
 subprocess.run(['python','-B','E:/work/image/qdao_original_roster_v13/tools/pipeline.py','import-walk','--character','01_ice_sword_girl','--direction','S','--rows','2','--cols','2','--output-frames',mapping,'--source',str(d/'raw.png'),'--prompt',str(d/'prompt.txt'),'--receipt',str(d/'tool-result.json'),'--batch-id',batch],check=True)
