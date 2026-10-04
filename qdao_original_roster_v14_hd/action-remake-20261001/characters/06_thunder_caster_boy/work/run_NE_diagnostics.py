import json,hashlib,statistics
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted((ROOT/'runtime/run/NE').glob('*.png'))
sheet=Image.new('RGB',(1380,772),(33,49,55));draw=ImageDraw.Draw(sheet)
audit=[];issues=[];sources=[]
reconstructed={}
for oldnative in (ROOT/'work').glob('run_NE_*.png'):
 try:
  oldim=Image.open(oldnative).convert('RGBA')
  if oldim.size!=(1254,1254):continue
  b=BytesIO();oldim.resize((1024,1024),Image.Resampling.LANCZOS).save(b,format='PNG')
  reconstructed[hashlib.sha256(b.getvalue()).hexdigest()]=oldnative
 except OSError:continue
for p in files:
 i=int(p.stem);im=Image.open(p);im.load();r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
 nr=ROOT/r['derivedFrom'][0]['generationRecord'];n=json.loads(nr.read_text(encoding='utf-8'));np=ROOT/n['file']
 row={'frame':i,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'nativeFile':n['file'],'nativeSHA':sha(np),'actualModel':n.get('actualModel'),'actualQuality':n.get('actualQuality')}
 if row['sha256']!=r['sha256'] or row['nativeSHA']!=r['derivedFrom'][0]['sha256'] or row['nativeSHA']!=n['sha256']:issues.append({'frame':i,'issue':'SHA mismatch'})
 if im.size!=(1024,1024) or im.mode!='RGBA' or im.getchannel('A').getextrema()[0]!=0:issues.append({'frame':i,'issue':'runtime format'})
 row['historicalReferences']=[]
 for ref in n['references']:
  refp=Path(ref['path']);refp=refp if refp.is_absolute() else ROOT/refp
  if not refp.exists() or sha(refp)!=ref['sha256']:
   recovered=False
   if refp.is_relative_to(ROOT) and refp.parent==ROOT/'runtime/run/NE':
    for hist in (ROOT/'records').glob(f'run_NE_{refp.stem}_replaced_by_*.json'):
     h=json.loads(hist.read_text(encoding='utf-8'))
     if h.get('sha256')!=ref['sha256']:continue
     oldnative=ROOT/h['derivedFrom'][0]['file']
     if not oldnative.exists():continue
     b=BytesIO();Image.open(oldnative).resize((1024,1024),Image.Resampling.LANCZOS).save(b,format='PNG')
     if hashlib.sha256(b.getvalue()).hexdigest()==ref['sha256']:
      row['historicalReferences'].append({'submittedPath':str(refp),'submittedSHA':ref['sha256'],'historyRecord':hist.relative_to(ROOT).as_posix(),'sourceNative':oldnative.relative_to(ROOT).as_posix(),'reconstruction':'Whole canvas Lanczos 1024 PNG exactly matches submitted SHA; no backup image written.'});recovered=True;break
   if not recovered and refp.is_relative_to(ROOT) and refp.parent==ROOT/'runtime/run/NE' and ref['sha256'] in reconstructed:
    oldnative=reconstructed[ref['sha256']]
    row['historicalReferences'].append({'submittedPath':str(refp),'submittedSHA':ref['sha256'],'sourceNative':oldnative.relative_to(ROOT).as_posix(),'sourceNativeSHA':sha(oldnative),'reconstruction':'Whole canvas Lanczos 1024 PNG exactly matches submitted SHA; current runtime was later replaced; original submitted path/hash remain unchanged. No backup image written.'})
    recovered=True
   if not recovered:issues.append({'frame':i,'issue':'reference missing or mismatch','reference':str(refp)})
 if 1<=i<=6 and 'prompt' not in n.get('submittedParameters',{}):
  pv=n.get('prompt','');n['submittedParameters']['prompt']=(ROOT/pv).read_text(encoding='utf-8-sig') if pv.startswith('prompts/') else pv
  nr.write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 audit.append(row);sources.append({'frame':i,'file':row['file'],'sha256':row['sha256']})
 cr=im.crop((180,690,870,1024)).resize((345,167),Image.Resampling.LANCZOS)
 x=i%4*345;y=i//4*193;sheet.paste(cr,(x,y),cr)
 draw.line((x,y+(942-690)//2,x+344,y+(942-690)//2),fill=(186,159,90))
 draw.text((x+8,y+171),f'NE / {i:02d}  same crop',fill=(248,240,218))
 # Fixed manually selected boot windows; diagnostics only, never used to align images.
 if i in [0,1,2,3]:window=(580,850,705,1000)
 elif i in [8,9,10,11]:window=(335,850,460,1000)
 else:window=None
 if window:
  a=im.getchannel('A');xs=[]
  for xx in range(window[0],window[2]):
   ys=[yy for yy in range(window[1],window[3]) if a.getpixel((xx,yy))>=128]
   if ys:xs.append(max(ys))
  row['bootWindow']=list(window);row['lowerContourMedian']=statistics.median(xs) if xs else None;row['lowerContourMax']=max(xs) if xs else None
sheet.save(ROOT/'review/run_NE_feet_contact_20261003.png')
(ROOT/'review/run_NE_feet_contact_20261003.json').write_text(json.dumps({'operation':'Fixed crop (180,690,870,1024), same 0.5 preview scale; line 942 provisional only. Runtime unchanged.','sources':sources},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out={'scope':'NE current exported frames only','frames':len(files),'target':16,'missing':[i for i in range(16) if not (ROOT/'runtime/run/NE'/f'{i:02d}.png').exists()],'uniqueNative':len({r['nativeSHA'] for r in audit})==len(audit),'issues':issues,'rows':audit,'rootVerified':False,'dynamicVerified':False,'clientIntegrated':False,'note':'Contour windows are diagnostics only, not verified contact point, no bbox/root alignment performed.'}
(ROOT/'review/run_NE_source_audit_20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
