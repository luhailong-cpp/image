import sys,json,hashlib,datetime,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';n=z/'native';pre='external-r08c04-1017-v8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def wr(p,data):assert not p.exists();p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
sp=importlib.util.spec_from_file_location('rc',q/'repair-compose.py');rc=importlib.util.module_from_spec(sp);sp.loader.exec_module(rc)
sp=importlib.util.spec_from_file_location('sh',z/'tools/seam_helpers.py');sh=importlib.util.module_from_spec(sp);sp.loader.exec_module(sh)
records=[]
for key,bounds,margin in [('e',[100,220,1254,850],90),('f',[600,610,1100,1030],85)]:
 stem='r08_c04_repair_'+key+'_external_1017_v2';req=json.loads((n/(stem+'.request.json')).read_text());native=n/(stem+'.png');src=Path(req['references'][0]['path']);assert sha(src)==req['references'][0]['sha256'];old=np.array(Image.open(src).convert('RGB'));im=Image.open(native);assert im.size==(1254,1254);new=np.array(im.convert('RGB'))
 gen={'file':native.as_posix(),'sha256':sha(native),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin returned no actual model metadata','submittedParameters':req['submittedParameters'],'references':req['references'],'coordinates':req['coordinates'],'prompt':req['prompt'],'receipt':ref(n/(stem+'.receipt.json')),'status':'candidate_pending_seam_qa','nativePixelsResampled':False}
 gp=Path(str(native)+'.generation.json');wr(gp,gen)
 mask,paths=rc.closed_mask(old,new,bounds,margin,req['coordinates']['tileContextBox'],sh._minimum_vertical_seam);after=np.where(mask[:,:,None].astype(bool),new,old)
 ap=q/(pre+'-'+key+'2-after-1254.png');assert not ap.exists();Image.fromarray(after).save(ap)
 mp=q/(pre+'-'+key+'2-mask.npy');assert not mp.exists();np.save(mp,mask,allow_pickle=False)
 records.append({'id':key+'2','source':req['references'][0],'native':ref(native),'generation':ref(gp),'after':ref(ap),'mask':ref(mp),'bounds':bounds,'margin':margin,'tileContextBox':req['coordinates']['tileContextBox'],'paths':paths})
p=q/(pre+'-local-preparation.json');wr(p,{'status':'pending_visual_qa','baseTrace':ref(q/'external-r08c04-1017-v7-trace.json'),'repairs':records,'script':ref(Path(__file__))});print(json.dumps({'manifest':ref(p),'after':[r['after'] for r in records]}))

