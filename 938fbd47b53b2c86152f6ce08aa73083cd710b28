from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,importlib.util,numpy as np
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');D=P/'lanxian_day/triple_r08_c06_c08';R=D/'repairs_v2';O=D/'output_v2';Q=D/'qa_v2';F=D/'registration_v2'
for d in (O,Q,F):d.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def w(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('r',P/'tools/mechanical_join.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
prev=j(D/'output_v1/assembly.json');a=np.array(Image.open(prev['triple']).convert('RGB'));original=a.copy();records=[]
for job in j(R/'plan.json')['jobs']:
 name=job['id'];native=np.array(Image.open(R/'native'/f'{name}.png').convert('RGB'));rec=j(R/'native'/f'{name}.record.json');assert sha(rec['sourceOutputPath'])==sha(R/'native'/f'{name}.png')==rec['outputSha256'];sx,sy,_,_=job['rectTripleXYXY']
 box=(200,0,1054,1254) if name!='short_edge' else (400,540,820,820);l,t,r,b=box;patch=native[t:b,l:r].copy();x,y=sx+l,sy+t;h,ww=patch.shape[:2];yy,xx=np.mgrid[:h,:ww]
 ds=[xx,ww-1-xx];edges=['left','right']
 if y>0:ds.append(yy);edges.append('top')
 if y+h<4096:ds.append(h-1-yy);edges.append('bottom')
 width=90 if name!='short_edge' else 32;mask=np.uint8(np.clip(np.minimum.reduce(ds)/width,0,1)*255);context=a[y:y+h,x:x+ww].copy();small=name=='short_edge'
 res,flow,col,report=m.registered_join(context,patch,mask,edges=edges,flow_inner=90 if small else 200,flow_full=28 if small else 65,tone_inner=110 if small else 230,tone_full=45 if small else 90)
 a[y:y+h,x:x+ww]=res;np.savez_compressed(F/f'{name}.fields.npz',flow=flow,colorCorrection=col,mask=mask);w(F/f'{name}.json',report)
 records.append({'id':name,'record':str(R/'native'/f'{name}.record.json'),'recordSha256':sha(R/'native'/f'{name}.record.json'),'sourceCropNativeXYXY':list(box),'rectTripleXYXY':[x,y,x+ww,y+h],'registration':report,'fields':str(F/f'{name}.fields.npz'),'fieldsSha256':sha(F/f'{name}.fields.npz')})
assert np.array_equal(a[:,:4096],original[:,:4096]);art=Image.fromarray(a);f=O/'triple.png';assert not f.exists();art.save(f);ext=Image.open(D/'output_v1/extended-context.png').convert('RGB');ext.paste(art,(115,115));ext.save(O/'extended-context.png')
for i,c in enumerate(prev['candidates']):
 p=O/f"{c['tile']}.png";e=O/f"{c['tile']}.extended.png";art.crop((i*4096,0,(i+1)*4096,4096)).save(p);ex=ext.crop((i*4096,0,i*4096+4326,4326));ex.save(e);assert np.array_equal(np.array(ex.crop((115,115,4211,4211))),np.array(Image.open(p)));c.update({'file':str(p),'sha256':sha(p),'extendedContext':str(e),'extendedContextSha256':sha(e)})
assert np.array_equal(np.concatenate([np.array(Image.open(c['file'])) for c in prev['candidates']],axis=1),a)
prev.update({'status':'repair_v2_pending_visual_QA','previousAssembly':str(D/'output_v1/assembly.json'),'previousAssemblySha256':sha(D/'output_v1/assembly.json'),'triple':str(f),'tripleSha256':sha(f),'extendedContext':str(O/'extended-context.png'),'extendedContextSha256':sha(O/'extended-context.png'),'repairs':records,'sourceResampling':'limited local edge registration <=8px; fields retained; native interiors unchanged','splitPixelIdentityPassed':True,'c06PixelsUnchangedFromV6':True});w(O/'assembly.json',prev)
art.resize((1800,600),Image.Resampling.LANCZOS).save(Q/'overview.jpg',quality=90)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);sheet=Image.new('RGB',(1240,1060),'white');ImageDraw.Draw(sheet).text((4,4),'lanxian_day c07/c08 repaired full seam; 1:1 segments 0..3',fill='black',font=font)
for seg in range(4):sheet.paste(art.crop((8042,seg*1024,8342,(seg+1)*1024)),(seg*310,36))
sheet.save(Q/'c07-c08-full-seam.png');sheet.save(Q/'c07-c08-full-seam.jpg',quality=94)
for job in j(R/'plan.json')['jobs']:
 sample=art.crop(job['rectTripleXYXY']);sample.save(Q/f"{job['id']}-return.png");sample.save(Q/f"{job['id']}-return.jpg",quality=94)
for y in (1024,2048,3072):art.crop((7742,y-450,8642,y+450)).save(Q/f'boundary-intersection-y{y}.png')
print('5 repairs applied to narrow ROIs; c06 unchanged; exact reconstruction passed')