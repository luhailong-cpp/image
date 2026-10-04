import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
outdir=ROOT/'provenance/run-northeast'
entries=[]
contact=Image.new('RGB',(1200,1320),(225,231,234));d=ImageDraw.Draw(contact)
versions={i:(2 if i in [1,4,5,6,7,8,9,13,16] else 1) for i in range(1,17)}
for i,v in versions.items():
 p=ROOT/f'staging/run/NE/{i:02d}-v{v}.png'; im=Image.open(p);im.load();a=im.getchannel('A')
 sha=hashlib.sha256(p.read_bytes()).hexdigest();rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 edge=list(a.crop((0,0,im.width,1)).getdata())+list(a.crop((0,im.height-1,im.width,im.height)).getdata())+list(a.crop((0,0,1,im.height)).getdata())+list(a.crop((im.width-1,0,im.width,im.height)).getdata())
 entries.append({'index':i,'file':str(p.relative_to(ROOT)),'absolutePath':str(p.resolve()),'generationRecord':str(Path(str(p)+'.generation.json').relative_to(ROOT)),'sha256':sha,'size':im.size,'mode':im.mode,'alphaRange':a.getextrema(),'opaqueEdgePixels':sum(x>8 for x in edge),'recordSHAMatches':sha==rec['sha256'],'singleFrameViewed':True,'phaseStatus':'reviewed_candidate'})
 thumb=im.copy();thumb.thumbnail((300,300));x=(i-1)%4*300;y=(i-1)//4*330;contact.paste(thumb,(x,y+30),thumb);d.text((x+8,y+8),f'NE {i:02d} v{v}',fill=(15,30,45))
data={'action':'run','direction':'NE','scope':'readall16;locallyrepair05/06/07/08','frames':entries,'actualPlaybackReviewed':False,'clientReview':'not_performed','allRecordsMatch':all(x['recordSHAMatches'] for x in entries),'allNative1254RGBA':all(x['size']==(1254,1254) and x['mode']=='RGBA' for x in entries),'remaining':['Parent normal/slow playback andclientgroundingreview notperformed'],'repaired07':'Rightbootremainsfolded/raised;leftbootmovesbetween06and08;noartificialwholecanvasalignment','kept13Reason':'13-v2 reads as lefttoeoff andrightkneeearlyrecovery; less urgent than05/06/08 wronglegphase.'}
(outdir/'NE-phaseaudit-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(outdir/'NE-selection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
cp=outdir/'NE-phaseaudit-contact.jpg';contact.save(cp,quality=92)
Path(str(cp)+'.generation.json').write_text(json.dumps({'file':str(cp.relative_to(ROOT)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'operation':'contactsheetwholecanvasresize300;noposeedits','derivedFrom':entries,'notGameAsset':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if k!='frames'},ensure_ascii=False))

