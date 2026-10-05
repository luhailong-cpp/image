from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
O=R/'full-limb-review-20261004'/'sw-nw-local-qa'
O.mkdir(exist_ok=True)
sets={
'sw-candidates':[('SW13','runtime/run/SW/13.png'),('SW14','runtime/run/SW/14.png'),('SW15 orig','runtime/run/SW/15.png'),('SW15 v1','full-limb-review-20261004/run-SW/15-v1/native.png'),('SW16 orig','runtime/run/SW/16.png'),('SW16 v2','full-limb-review-20261004/run-SW/16-v2/native.png')],
'nw-candidates':[('NW15 orig','runtime/run/NW/15.png'),('NW15 v1','full-limb-review-20261004/run-NW-south/15-v1/native.png'),('NW16 orig','runtime/run/NW/16.png'),('NW16 v1','full-limb-review-20261004/run-NW-south/16-v1/native.png')]
}
out={}
for name,items in sets.items():
 w=420; canvas=Image.new('RGB',(w*len(items),w+35),(50,55,60));d=ImageDraw.Draw(canvas);recs=[]
 if name=='sw-candidates': items[-1]=('SW16 v3','full-limb-review-20261004/run-SW/16-v3/native.png')
 if name=='nw-candidates': items[1]=('NW15 v2','full-limb-review-20261004/run-NW-south/15-v2/native.png');items[-1]=('NW16 v4','full-limb-review-20261004/run-NW-south/16-v4/native.png')
 for i,(label,path) in enumerate(items):
  p=R/path;im=Image.open(p).convert('RGBA').resize((w,w),Image.Resampling.LANCZOS);canvas.paste(im,(i*w,35),im);d.text((i*w+10,10),label,fill='white')
  recs.append({'label':label,'file':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 canvas.save(O/(name+'.jpg'),quality=95);out[name]=recs
(O/'sources.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(str(O))
