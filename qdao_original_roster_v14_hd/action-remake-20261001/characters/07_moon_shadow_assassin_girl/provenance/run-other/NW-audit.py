import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
DIR=ROOT/'staging/run/NW'
selected={i:DIR/(f'{i:02d}-v2.png' if i in [2,3,4,5,6,10,11,12] else f'{i:02d}.png') for i in range(1,17)}
entries=[]
contact=Image.new('RGB',(1200,1320),(225,231,234)); d=ImageDraw.Draw(contact)
for i,p in selected.items():
 im=Image.open(p); im.load(); alpha=im.getchannel('A')
 sha=hashlib.sha256(p.read_bytes()).hexdigest(); rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 perimeter=list(alpha.crop((0,0,im.width,1)).getdata())+list(alpha.crop((0,im.height-1,im.width,im.height)).getdata())+list(alpha.crop((0,0,1,im.height)).getdata())+list(alpha.crop((im.width-1,0,im.width,im.height)).getdata())
 ent={'index':i,'file':str(p.relative_to(ROOT)),'generationRecord':str(Path(str(p)+'.generation.json').relative_to(ROOT)),'sha256':sha,'recordSHAMatches':sha==rec['sha256'],'width':im.width,'height':im.height,'mode':im.mode,'alphaRange':alpha.getextrema(),'opaqueEdgePixels':sum(x>8 for x in perimeter),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'static':'reviewed_candidate','dynamic':'pending'}
 entries.append(ent)
 thumb=im.copy();thumb.thumbnail((300,300)); x=((i-1)%4)*300;y=((i-1)//4)*330;contact.paste(thumb,(x,y+30),thumb);d.text((x+8,y+8),f'NW {i:02d} '+p.stem,fill=(15,30,45))
summary={'direction':'NW','frames':entries,'selectedCount':len(entries),'allNativeHD':all(e['width']>=1024 and e['height']>=1024 for e in entries),'uniqueSHA':len({e['sha256'] for e in entries}),'allRecordsMatch':all(e['recordSHAMatches'] for e in entries),'allNoOpaqueCanvasClipping':all(e['opaqueEdgePixels']==0 for e in entries),'visualReview':{'singleFrameReview':'all16 viewed','sequenceReview':'pending_parent','clientReview':'not_performed'}}
out=ROOT/'provenance/run-other/NW-selection.json';out.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
cp=ROOT/'provenance/run-other/NW-contact.jpg';contact.save(cp,quality=92)
Path(str(cp)+'.generation.json').write_text(json.dumps({'file':str(cp.relative_to(ROOT)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'operation':'review contact sheet; whole canvas fit to300 withnoimageposeediting','derivedFrom':entries,'notGameAsset':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='frames'},ensure_ascii=False))

