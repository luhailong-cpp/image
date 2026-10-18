from pathlib import Path
from PIL import Image
import json,hashlib,datetime,sys
B=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mode=sys.argv[1]
if mode=='prepare':
 spec=json.loads(sys.stdin.read());base=B/spec['base'];j=json.loads(base.read_text(encoding='utf-8-sig'));source=base.parent/j['context']['path'];box=spec['box'];rid=spec['id'];version=spec.get('version',1)
 crop=D/(rid+f'-v{version:02d}.source-native-crop.png');assert not crop.exists();Image.open(source).crop(box).save(crop)
 gb=[j['globalContextBox'][i%2]+box[i] for i in range(4)]
 q={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batch':'village-west-courtyard','tile':'r12_c07','repairId':rid,'attempt':version,'source':{'path':str(source),'sha256':sha(source),'contextCropBox':box},'baseAssembly':{'path':str(base),'sha256':sha(base)},'references':[{'path':str(crop),'sha256':sha(crop),'role':'edit target: actual integer native crop, no resize'}],'globalNativeBox':gb,'globalCoreBox':[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115],'coreInNative':[115,115,1139,1139],'arguments':{'prompt':spec['prompt'],'referenced_image_paths':[str(crop)],'transparent_background':False},'route':'builtin','actualModel':None,'actualQuality':None,'status':'prepared','formalAccepted':False,'instructionsSha256':sha(Path('D:/work/image/AGENTS.md')),'splitSha256':sha(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'))}
 qp=D/(rid+f'-v{version:02d}.request.json');qp.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'request':str(qp),'crop':str(crop),'globalNativeBox':gb}))
elif mode=='qa':
 d=B/sys.argv[2];a=json.loads((d/'assembly.json').read_text());im=Image.open(d/'context-native.png');x,y,x1,y1=a['repairOverlay']['contextBox'];boxes={'top':[x,max(0,y-115),x1,y+345],'bottom':[x,y1-345,x1,min(im.height,y1+115)],'left':[max(0,x-115),y,x+345,y1],'right':[x1-345,y,min(im.width,x1+115),y1]}
 for k,v in boxes.items():
  p=d/(k+'-boundary-native.png');assert not p.exists();im.crop(v).save(p)
 print(json.dumps(boxes))
elif mode=='review':
 spec=json.loads(sys.stdin.read());d=B/spec.pop('dir');a=json.loads((d/'assembly.json').read_text());spec.update(schemaVersion=1,tile='r12_c07',recordedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),assembly={'path':str(d/'assembly.json'),'sha256':sha(d/'assembly.json')},nativeScale=1,formalAccepted=False,externalQa='prior failures retained; other external seams unverified',sourceReplay=a['proof'])
 spec['reviewedCrops']=[{'path':str(d/p),'sha256':sha(d/p)} for p in ['repair-overlay-native.png','top-boundary-native.png','bottom-boundary-native.png','left-boundary-native.png','right-boundary-native.png']]
 p=d/'visual-qa-v1.json';assert not p.exists();p.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8');print(str(p))
