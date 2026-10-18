from pathlib import Path
import argparse,json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':str(p),'sha256':sha(p)}
p=argparse.ArgumentParser();p.add_argument('--assembly',required=True);p.add_argument('--id',required=True);p.add_argument('--x',type=int,required=True);p.add_argument('--y',type=int,required=True);p.add_argument('--prompt',required=True);p.add_argument('--attempt',type=int,default=1);a=p.parse_args()
bp=Path(a.assembly).resolve();assert bp.is_relative_to(B/'qa')
j=json.loads(bp.read_text(encoding='utf-8-sig'));assert j['scopeTiles']==['r13_c07']
src=bp.parent/j['context']['path'];assert sha(src)==j['context']['sha256']
out=B/'repairs'/'r13c07-internal-seams-oct16';out.mkdir(exist_ok=True)
stem=f'{a.id}-v{a.attempt:02d}';img=out/(stem+'.source-native-crop.png');req=out/(stem+'.request.json');assert not img.exists() and not req.exists()
box=[a.x,a.y,a.x+1254,a.y+1254];im=Image.open(src);assert min(box)>=0 and box[2]<=im.width and box[3]<=im.height
with img.open('xb') as f:im.crop(box).save(f,format='PNG')
ox,oy=j['globalContextBox'][:2];gb=[box[0]+ox,box[1]+oy,box[2]+ox,box[3]+oy];cb=[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115]
authorities=[Path('D:/work/image/AGENTS.md'),Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'),Path('C:/Users/luyua/.codex/skills/.system/imagegen/SKILL.md')]
q={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batch':'village-west-courtyard','tile':'r13_c07','repairId':a.id,'attempt':a.attempt,'source':{**ref(src),'contextCropBox':box},'baseAssembly':ref(bp),'references':[{**ref(img),'role':'actual native1254 integer crop edit target; no resizing'}],'authorities':[ref(t) for t in authorities],'globalNativeBox':gb,'globalCoreBox':cb,'coreInNative':[115,115,1139,1139],'prompt':a.prompt,'arguments':{'prompt':a.prompt,'referenced_image_paths':[str(img)],'transparent_background':False},'route':'builtin','actualModel':None,'actualQuality':None,'formalAccepted':False}
with req.open('x',encoding='utf-8') as f:json.dump(q,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'request':str(req),'source':str(img),'baseSha256':sha(bp),'globalNativeBox':gb}))
