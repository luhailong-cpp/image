from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
xs={'S':[540,527,529,537,554,534,556,541,530,518,526,523,532,528,533,526],'SW':[524,530,550,560,560,546,547,544,520,534,548,539,545,528,538,532],'SE':[570,575,580,595,600,592,590,571,580,600,615,584,593,580,589,578]}
for d,xx in xs.items():
 if len(sys.argv)>1 and d not in sys.argv[1:]: continue
 rec={'schemaVersion':1,'coordinateSpace':'1024 whole-canvas downsample BEFORE any global registration','targetRoot':[512,942],'globalScale':0.8,'applyTransform':False,'status':'provisional while pose repairs continue','method':'Manual pelvic center x projected to virtual ground. y=942 is fixed virtual plane, not lowest-foot alignment. Anatomical support and flight are kept in image. Current shoes may overrun target ground; painting and sequence verification pending.','frames':[]}
 for n,x in enumerate(xx,1):
  p=R/'run'/d/f'{n:02}.png'
  rec['frames'].append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'srcRoot':[x,942],'basis':'manual pelvis midpoint projection; excludes sleeves/fox/crystal, no bbox fitting','confidence':'approximate +/- 12px; sequence review pending'})
 (R/'run'/d/'registration.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')

