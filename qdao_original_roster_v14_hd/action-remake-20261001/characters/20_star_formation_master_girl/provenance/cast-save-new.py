from pathlib import Path
import json,sys,hashlib,subprocess
from PIL import Image
B=Path(__file__).resolve().parents[1]
job=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
dest=job['dest'];source=sys.argv[2];refs=job['refs']
subprocess.run([sys.executable,str(B/'tools/save_generation.py'),source,dest,job['prompt'],json.dumps(refs), '--status',job.get('status','pending_visual_review'),'--note',job.get('note','待实图检查；未动态验收')],check=True)
rp=B/(dest+'.generation.json');rec=json.loads(rp.read_text(encoding='utf-8'))
rec['references']=[{'path':r,'role':role,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r,role in zip(refs,job['roles'])]
rec['promptSha256']=hashlib.sha256((B/job['prompt']).read_bytes()).hexdigest()
im=Image.open(B/dest);rec['pixelValidation']={'alphaExtrema':im.getchannel('A').getextrema(),'alphaBBox':im.getchannel('A').getbbox(),'nativeSize':list(im.size),'transformation':'原生PNG原样复制，无裁切或缩放','globalAnchorAcceptance':False}
rec['evidence']['receipt']=job['receipt']
rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
