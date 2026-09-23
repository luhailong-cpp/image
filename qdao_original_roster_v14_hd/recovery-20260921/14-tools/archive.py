"""Export only character 14. Keeps temporary raw until final review/cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil, re
from PIL import Image
import numpy as np

REC=Path(__file__).resolve().parents[1]
GEN=REC/'14-generation'
DEST=REC/'14-delivery-preview/assets'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--original',type=Path);p.add_argument('--tool-result',type=Path);p.add_argument('--archive-only',action='store_true');p.add_argument('--replace-selected',action='store_true');p.add_argument('--target-edge',type=int,default=952);a=p.parse_args()
 arc=a.archive.resolve();assert arc.is_relative_to(GEN.resolve())
 req=read(arc/'request.json');actual=req.get('actual_request',req.get('request',req));assert (arc/'prompt.txt').read_text(encoding='utf-8-sig')==actual['prompt']
 result=read(a.tool_result or arc/'tool-result.json');hint=result.get('output_hint','');assert hint
 original=a.original
 if not original:
  matches=re.findall(r'[A-Za-z]:[^\r\n]*?exec-[0-9a-f-]+\.png',hint)
  matches=[m.split(' as ')[-1] for m in matches]
  original=Path(matches[-1]) if matches else None
 raw=arc/'raw.png'
 if original and original.is_file():
  assert str(original).replace('/','\\') in hint.replace('/','\\'),'Original path is absent from tool result'
  if raw.exists():assert sha(raw)==sha(original),'Existing raw differs'
  else:shutil.copy2(original,raw)
 assert raw.is_file(),'Missing real raw and original output'
 with Image.open(raw) as im:im.load();native=im.size;mode=im.mode;image=im.convert('RGBA')
 assert min(native)>=1024,'Native dimensions below requirement'
 alpha=np.asarray(image)[:,:,3];assert mode=='RGBA' and (alpha==0).mean()>.05 and (alpha>200).mean()>.05,'Not actual usable alpha'
 slot=req.get('slot');
 if not isinstance(slot,dict):
  m=re.match(r'(NE|NW|SE|SW|N|E|S|W)(idle|\d{2})',arc.name);assert m
  slot={'kind':'idle' if m[2]=='idle' else 'walk','direction':m[1],'frame':None if m[2]=='idle' else int(m[2])}
 record={'tool':'image_gen__imagegen','route':'builtin','file':'raw.png','sha256':sha(raw),'generatedAt':req.get('started_at',req.get('created_at')),'recordedAt':datetime.now(timezone.utc).isoformat(),'nativeSize':list(native),'nativeMode':mode,'configSnapshot':req.get('configSnapshot'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool did not expose model or quality.','actual_request':actual,'references':req.get('referenceBindings',[]),'output_hint':hint,'originalOutputPath':str(original) if original else None,'slot':slot,'generation_calls':1,'paid_api_calls':0,'sourceRetention':'temporary during production; delete after final selection under user instruction 2026-09-23'}
 write(arc/'raw.png.generation.json',record)
 if a.archive_only:print(json.dumps({'archived':str(arc),'nativeSize':native}));return
 assert 850<=a.target_edge<=952,'Export must remain a downsample within the approved framing range'
 scale=min(1.,a.target_edge/max(native));size=tuple(round(v*scale) for v in native);small=image.resize(size,Image.Resampling.LANCZOS)
 aa=np.asarray(small)[:,:,3];ys,xs=np.where(aa>8);assert len(xs)
 dx=(1024-size[0])//2;dy=942-int(ys.max());bbox=(int(xs.min())+dx,int(ys.min())+dy,int(xs.max())+dx,int(ys.max())+dy)
 assert 0<=bbox[0] and 0<=bbox[1] and bbox[2]<1024 and bbox[3]<1024,'Anchor alignment clips content'
 canvas=Image.new('RGBA',(1024,1024));canvas.paste(small,(dx,dy))
 d=slot['direction'];kind=slot['kind'];relative=f'idle/{d}.png' if kind=='idle' else f'walk/{d}/{int(slot["frame"]):02d}.png'
 out=DEST/relative
 assert not out.exists() or a.replace_selected,'Existing selected asset: replacement requires explicit selection'
 out.parent.mkdir(parents=True,exist_ok=True);canvas.save(out)
 record.update({'file':relative,'sha256':sha(out),'width':1024,'height':1024,'format':'PNG','derivedFrom':{'sha256':sha(raw),'nativeSize':list(native),'temporaryRaw':str(raw)},'operation':{'type':'whole-image downsample and integer sole anchor alignment','scale':scale,'translation':[dx,dy],'soleY':942,'noPoseSynthesis':True,'noUpscale':True},'visualReview':'pending','sourceArchive':arc.name})
 write(str(out)+'.generation.json',record)
 print(json.dumps({'output':str(out),'sha256':sha(out),'source':arc.name,'nativeSize':native,'bbox':bbox,'visualReview':'pending'}))
if __name__=='__main__':main()
