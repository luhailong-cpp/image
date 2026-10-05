from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path("D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
D=R/'full-limb-review-20261004/run-NW-east';D.mkdir(exist_ok=True)
picks={'02':'02-v3','03':'03-v1','05':'05-v1','06':'06-v2'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bg(im):
 b=Image.new('RGBA',im.size,(35,41,53,255));b.alpha_composite(im);return b.convert('RGB')
frames=[]
for n,v in picks.items():
 original=R/'runtime/run/NW'/f'{n}.png'
 native=R/'full-limb-review-20261004/run-NW'/v/'native.png'
 before=Image.open(original).convert('RGBA');after=Image.open(native).convert('RGBA')
 out=after.resize((1024,1024),Image.Resampling.LANCZOS)
 out.save(native.parent/'review1024.png')
 sheet=Image.new('RGB',(960,916),(24,29,39));d=ImageDraw.Draw(sheet)
 for i,(name,im) in enumerate([('CURRENT RUNTIME',before),('CORRECTED '+v,out)]):
  d.text((i*480+12,10),name,fill='white')
  sheet.paste(bg(im).resize((480,480),Image.Resampling.LANCZOS),(i*480,32))
  crop=im.crop((280,575,840,1030))
  sheet.paste(bg(crop).resize((480,390),Image.Resampling.LANCZOS),(i*480,526))
 sheet.save(D/f'{n}-before-after.jpg',quality=95)
 frames.append({'slot':'run/NW/'+n,'original':original.relative_to(R).as_posix(),'originalSHA256':sha(original),'selected':native.relative_to(R).as_posix(),'selectedSHA256':sha(native),'nativeSize':list(after.size),'nativeMode':after.mode,'reviewExport':(native.parent/'review1024.png').relative_to(R).as_posix(),'reviewExportSHA256':sha(native.parent/'review1024.png'),'reviewStatus':'pending-final-view'})
(D/'frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(frames,ensure_ascii=False))

