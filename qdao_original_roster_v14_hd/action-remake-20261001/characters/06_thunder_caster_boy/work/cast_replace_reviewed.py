import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for direction,frame in [('W',5),('W',6)]:
 stem=f'cast_{direction}_{frame:02d}'
 native=ROOT/'work'/f'{stem}_v2.png'
 nrec=native.with_name(native.name+'.generation.json')
 rec=json.loads(nrec.read_text(encoding='utf-8'))
 out=ROOT/'runtime'/'cast'/direction/f'{frame:02d}.png'
 orec=out.with_name(out.name+'.generation.json')
 old=json.loads(orec.read_text(encoding='utf-8'))
 im=Image.open(native);im.load()
 assert im.mode=='RGBA' and im.size==(1254,1254) and im.getchannel('A').getextrema()==(0,255)
 archived=ROOT/'records'/f'{stem}_v1_runtime_superseded.json'
 old['supersededBy']=f'work/{stem}_v2.png.generation.json'
 old['supersededReason']='近侧靴向镜头/外撇，局部改为随角色面向；站距和上身保留；旧图片按用户素材保留要求删除，文字哈希和来源保留'
 archived.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 sha=hashlib.sha256(out.read_bytes()).hexdigest()
 outrec={**old,'sha256':sha,'derivedFrom':[{'file':rec['file'],'sha256':rec['sha256'],'generationRecord':nrec.relative_to(ROOT).as_posix()}],'native':rec['native'],'visualReview':rec['visualReview'],'generatedAt':rec['generatedAt'],'replacesRecord':archived.relative_to(ROOT).as_posix()}
 outrec.pop('supersededBy',None);outrec.pop('supersededReason',None)
 orec.write_text(json.dumps(outrec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rec['exported']=True;rec['exportPath']=out.relative_to(ROOT).as_posix()
 nrec.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Only remove the explicitly superseded native after the new export and records exist.
 oldnative=(ROOT/'work'/f'{stem}_v1.png').resolve()
 assert oldnative.is_relative_to(ROOT.resolve()) and out.exists() and orec.exists()
 oldnrec=oldnative.with_name(oldnative.name+'.generation.json')
 if oldnrec.exists():
  nr=json.loads(oldnrec.read_text(encoding='utf-8'));nr['retention']={'imageRemoved':True,'reason':'superseded by reviewed v2; source text and hash retained','at':datetime.now(timezone.utc).isoformat(),'replacement':rec['file']};oldnrec.write_text(json.dumps(nr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if oldnative.exists():oldnative.unlink()
 print(out.relative_to(ROOT),sha)
