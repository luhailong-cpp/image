import sys,json,hashlib,importlib.util,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('export_frame',R/'tools/export_frame.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sourceRows=json.loads((R/'provenance/north-bamboo-native-sources.json').read_text(encoding='utf-8'))
batch=int(sys.argv[1])
rcs=json.loads((R/'provenance'/f'north-bamboo-batch{batch}-receipts.json').read_text(encoding='utf-8'))
for rc in rcs:
 q=rc['q'];d=q['direction'];f=q['frame'];ident=q['id'];src=R/'run/staging'/f'{ident}.png';dst=R/'run/staging'/f'{ident}-registered.png'
 row=next(x for x in sourceRows if x['direction']==d and x['frame']==f)
 sr=q.get('registrationSourceRoot') or row.get('oldGenerationRecord',{}).get('registrationTransform',{}).get('sourceRoot') or row['oldRegistrationRow']['srcRoot']
 m.run(src,dst);im=Image.open(dst).convert('RGBA');pre=sha(dst);s=.8;tx=round(512-s*sr[0]);ty=round(942-s*sr[1])
 out=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA');out.save(dst)
 p=Path(str(dst)+'.generation.json');rec=json.loads(p.read_text(encoding='utf-8'))
 rec['sha256']=sha(dst);rec['actualModel']=None;rec['actualQuality']=None
 rec['registrationTransform']={'method':'one global affine scale; native identity master anatomical root reused after edit; no per-frame bbox fitting or sole alignment','globalScale':.8,'sourceRoot':sr,'targetRoot':[512,942],'integerTranslation':[tx,ty],'inputSha256':pre,'outputSha256':sha(dst),'inputNativeReferenceSha256':sha(q['params']['referenced_image_paths'][0]),'inputOriginalRegisteredReferenceSha256':row['oldFormalSha256'],'registrationFile':f'run/{d}/registration.json','sourceRootBasis':'N01 native master root' if q.get('registrationSourceRoot') else 'original same-frame native anatomical root','recordedAt':datetime.now(timezone.utc).isoformat()}
 rec['review']={'status':'pending_visual_review'};p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 gr=Path(str(src)+'.generation.json');g=json.loads(gr.read_text(encoding='utf-8'));g['references'][0]['role']='original native edit target and identity; before scale registration';g['canvasMode']=q['canvasMode'];gr.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(4*360,((len(rcs)+1)//2)*390),'#758082');draw=ImageDraw.Draw(sheet)
for i,rc in enumerate(rcs):
 q=rc['q'];d=q['direction'];f=q['frame'];ident=q['id'];paths=[R/'run'/d/(f+'.png'),R/'run/staging'/f'{ident}-registered.png']
 for k,p in enumerate(paths):
  im=Image.open(p).convert('RGBA').resize((360,360),Image.Resampling.LANCZOS);x=(i%2*2+k)*360;y=i//2*390;sheet.paste(im,(x,y+25),im);draw.text((x+10,y+7),f'{d}{f} '+('old/current' if k==0 else 'native repair'),fill='white')
sheet.save(R/'run/staging'/f'north-bamboo-batch{batch}-comparison.jpg')
print('Exported candidates '+str(len(rcs)))

