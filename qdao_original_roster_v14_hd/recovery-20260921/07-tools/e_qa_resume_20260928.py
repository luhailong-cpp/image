from pathlib import Path
from PIL import Image, ImageSequence
from datetime import datetime,timezone
import json,hashlib,numpy as np
HERE=Path(__file__).resolve().parent
SRC=HERE/'candidate/07_moon_shadow_assassin_girl'
OUT=HERE/'e-review-20260928'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for slot in ['idle/E.png']+[f'walk/E/{i:02}.png' for i in range(1,17)]:
 p=SRC/slot;m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p);a=np.asarray(im.getchannel('A'))
 raw=Path(m['derivedFrom']['path']);req=Path(m['requestEvidence']['path']);res=Path(m['resultEvidence']['path'])
 rows.append({'slot':slot,'sha256':sha(p),'attempt':m['attempt'],'sourceSha256':sha(raw),'nativeSize':list(Image.open(raw).size),'nativeMatchesRecord':sha(raw)==m['derivedFrom']['sha256'],'outputMatchesRecord':sha(p)==m['outputSha256'],'size':list(im.size),'mode':im.mode,'footBottomAlphaGt8':int(np.where(a>8)[0].max()),'edgeAlphaMax':max(int(x.max()) for x in [a[0],a[-1],a[:,0],a[:,-1]]),'requestMatchesRecord':sha(req)==m['requestEvidence']['sha256'],'resultMatchesRecord':sha(res)==m['resultEvidence']['sha256'],'actualModel':m['actualModel'],'actualQuality':m['actualQuality']})
 name=p.stem
 pair=Image.new('RGB',(2048,1024))
 for k,bg in enumerate([(30,38,46),(240,238,228)]):
  b=Image.new('RGB',im.size,bg);b.paste(im,(0,0),im);pair.paste(b,(1024*k,0))
 pair.save(OUT/'qa'/f'{name}-pair.png')
gifs=[]
for gp in [OUT/'E-30ms-dark.gif',OUT/'E-30ms-light.gif']:
 g=Image.open(gp);d=[f.info.get('duration') for f in ImageSequence.Iterator(g)]
 gifs.append({'file':gp.name,'sha256':sha(gp),'frames':len(d),'durationMs':d,'cycleMs':sum(d),'timingPass':d==[30]*16})
report={'observedAt':datetime.now(timezone.utc).isoformat(),'scope':'07 E only','files':rows,'gifs':gifs,'uniqueOutputSha':len(set(r['sha256'] for r in rows)),'uniqueNativeSha':len(set(r['sourceSha256'] for r in rows)),'staticVisualReview':{'contactLightDark':True,'all17At1024LightDark':True,'seam15160102LightDarkAt512':True,'replacementE13At1024LightDark':False,'findings':['E13 upper-body camera, excessive scarf length and hard outline repaired by a genuine native1254 single-image edit; current selection walk-E-13-continuity-r20260928a.','Anatomical left hair ornament correctly hidden on far side for E; tiny navy/gold tip only.','E01-04: rear square-marked leg lifts and passes while diamond-marked leg supports. E05-09: square leg swings forward and lowers; diamond supports. E10-12: opposite leg lifts and passes with near square leg supporting. E13-16: far leg swings forward toward the next contact.','Support foot baseline alpha>8 is y942 in all17 exports. Head silhouette and scarf move independently rather than mechanically shifted whole poses.','No clipped weapon, hair, scarf or foot; no visible detached high-alpha remnants in inspected deep/light pairs.','E06 high knee / E11 rear flex are stylized pronounced gait poses. The live480ms cycle still requires browser assessment for their transitions.']},'browserPlaybackPerformedByThisAgent':False,'offlineArtAcceptance':'pending_live_review','clientIntegration':False}
(OUT/'qa-resume-20260928.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(OUT/'qa-resume-20260928.json'),'allRowsVerified':all(r['nativeMatchesRecord'] and r['outputMatchesRecord'] and r['requestMatchesRecord'] and r['resultMatchesRecord'] for r in rows),'uniqueNative':report['uniqueNativeSha'],'uniqueOutputs':report['uniqueOutputSha'],'footBaselines':sorted(set(r['footBottomAlphaGt8'] for r in rows)),'gifs':gifs}))
