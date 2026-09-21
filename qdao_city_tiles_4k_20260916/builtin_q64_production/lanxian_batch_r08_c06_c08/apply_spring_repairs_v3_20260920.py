# v3 preserves all four ROI edges, including the tile top/bottom, using the same four native repairs. Prior outputs remain untouched.
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,importlib.util,numpy as np
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');D=P/'lanxian_spring/triple_r08_c06_c08';R=D/'repairs_v2_20260920';O=D/'output_v3';Q=D/'qa_v3';F=D/'registration_v3'
assert not O.exists() and not Q.exists() and not F.exists(), 'Never overwrite an existing version'
for d in (O,Q,F):d.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def w(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('r',P/'tools/mechanical_join.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
prev=j(D/'output_v1/assembly.json');a=np.array(Image.open(prev['triple']).convert('RGB'));original=a.copy();records=[];touched=np.zeros(a.shape[:2],bool)
for job in j(R/'plan.json')['jobs']:
 name=job['id'];nf=R/'native'/f'{name}.png';native=np.array(Image.open(nf).convert('RGB'));rec=j(R/'native'/f'{name}.record.json');assert sha(rec['sourceOutputPath'])==sha(nf)==rec['outputSha256'];assert sha(rec['prompt'])==rec['promptSha256']
 for ref in rec['actualInputs']:assert sha(ref['path'])==ref['sha256']
 sx,sy,_,_=job['rectTripleXYXY'];box=(200,0,1054,1254);l,t,r,b=box;patch=native[t:b,l:r].copy();x,y=sx+l,sy+t;h,ww=patch.shape[:2];yy,xx=np.mgrid[:h,:ww]
 ds=[xx,ww-1-xx,yy,h-1-yy];edges=['left','right','top','bottom']
 mask=np.uint8(np.clip(np.minimum.reduce(ds)/95,0,1)*255);context=a[y:y+h,x:x+ww].copy()
 res,flow,col,report=m.registered_join(context,patch,mask,edges=edges,max_shift=8,flow_inner=180,flow_full=45,tone_inner=210,tone_full=65)
 a[y:y+h,x:x+ww]=res;touched[y:y+h,x:x+ww]|=mask>0
 np.savez_compressed(F/f'{name}.fields.npz',flow=flow,colorCorrection=col,mask=mask);w(F/f'{name}.json',report)
 records.append({'id':name,'record':str(R/'native'/f'{name}.record.json'),'recordSha256':sha(R/'native'/f'{name}.record.json'),'sourceCropNativeXYXY':list(box),'rectTripleXYXY':[x,y,x+ww,y+h],'registration':report,'fields':str(F/f'{name}.fields.npz'),'fieldsSha256':sha(F/f'{name}.fields.npz')})
assert np.array_equal(a[~touched],original[~touched]);assert np.array_equal(a[:,:4096],original[:,:4096]);art=Image.fromarray(a);f=O/'triple.png';art.save(f)
ext=Image.open(D/'output_v1/extended-context.png').convert('RGB');ext.paste(art,(115,115));ext.save(O/'extended-context.png')
for i,c in enumerate(prev['candidates']):
 p=O/f"{c['tile']}.png";e=O/f"{c['tile']}.extended.png";art.crop((i*4096,0,(i+1)*4096,4096)).save(p);ex=ext.crop((i*4096,0,i*4096+4326,4326));ex.save(e);assert np.array_equal(np.array(ex.crop((115,115,4211,4211))),np.array(Image.open(p)));c.update({'file':str(p),'sha256':sha(p),'extendedContext':str(e),'extendedContextSha256':sha(e)})
assert np.array_equal(np.concatenate([np.array(Image.open(c['file'])) for c in prev['candidates']],axis=1),a)
prev.update({'status':'repair_v3_four_edge_return_pending_visual_QA','previousAssembly':str(D/'output_v1/assembly.json'),'previousAssemblySha256':sha(D/'output_v1/assembly.json'),'triple':str(f),'tripleSha256':sha(f),'extendedContext':str(O/'extended-context.png'),'extendedContextSha256':sha(O/'extended-context.png'),'repairs':records,'sourceResampling':'limited local edge registration <=8px; fields retained; native interiors unchanged','splitPixelIdentityPassed':True,'c06PixelsUnchangedFromV6':True,'allPixelsOutsideRepairMasksUnchanged':True,'sourceUpscaledTo4K':False});w(O/'assembly.json',prev)
art.resize((1800,600),Image.Resampling.LANCZOS).save(Q/'overview.jpg',quality=92)
def seam_sheet(axis,coord,start,name):
 sheet=Image.new('RGB',(1240,1060),'white');ImageDraw.Draw(sheet).text((4,4),name+' full seam; 1:1 segments 0..3',fill='black')
 for seg in range(4):
  if axis=='v':im=art.crop((coord-150,start+seg*1024,coord+150,start+(seg+1)*1024))
  else:im=art.crop((start+seg*1024,coord-150,start+(seg+1)*1024,coord+150)).transpose(Image.Transpose.ROTATE_90)
  sheet.paste(im,(seg*310,36))
 sheet.save(Q/f'{name}.png')
seam_sheet('v',8192,0,'c07-c08-full-seam')
for val in (1024,2048,3072):
 seam_sheet('v',8192+val,0,f'c08-internal-x{val}')
 seam_sheet('h',val,8192,f'c08-internal-y{val}')
 seam_sheet('h',val,4096,f'c07-affected-internal-y{val}')
 art.crop((7742,val-450,8642,val+450)).save(Q/f'boundary-intersection-y{val}.png')
 for xx in (1024,2048,3072):art.crop((8192+xx-225,val-225,8192+xx+225,val+225)).save(Q/f'c08-junction-x{xx}-y{val}.png')
for rec in records:
 x,y,r,b=rec['rectTripleXYXY'];art.crop((x-100,max(0,y-100),r+100,min(4096,b+100))).save(Q/f"{rec['id']}-actual-roi-return.png")
art.crop((7950,250,8300,540)).save(Q/'upper-short-line-detail.png');art.crop((8150,2100,8450,2350)).save(Q/'lower-short-line-detail.png')
print('4 repair ROIs applied; source hashes, unchanged masks, c06 retention and split reconstruction passed; QA pending')

