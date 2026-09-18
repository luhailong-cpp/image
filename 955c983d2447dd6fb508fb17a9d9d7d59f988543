from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,importlib.util,sys
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');ap=sys.argv[1];t=P/ap/'r08_c08';out=P/ap/'triple_r08_c06_c08/output_v1';qa=out.parent/'qa_v1';out.mkdir(parents=True,exist_ok=True);qa.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def w(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=importlib.util.spec_from_file_location('a',t/'assemble_builtin_single_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=P/ap/'pair_r08_c06_c07/output/pair-extended-v6.png';new=t/'output/extended-context.png';a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(new).convert('RGB'));assert a.shape==(4326,8422,3);assert b.shape==(4326,4326,3)
a,metric=m.append_patch(a,b,m.load_seam_helper(),'c07_c08_230px_overlap');ext=Image.fromarray(a);art=ext.crop((115,115,12403,4211));assert art.size==(12288,4096)
f=out/'triple.png';assert not f.exists();art.save(f);ext.save(out/'extended-context.png');art.resize((1800,600),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=90)
prev=j(P/ap/'pair_r08_c06_c07/output/pair-v6-assembly.json');plan=j(t/'plan.json');candidates=[]
for i,col in enumerate((6,7,8)):
 tile=f'r08_c{col:02d}';cf=out/f'{tile}.png';ef=out/f'{tile}.extended.png';piece=art.crop((4096*i,0,4096*(i+1),4096));piece.save(cf);ep=ext.crop((4096*i,0,4096*i+4326,4326));ep.save(ef);assert np.array_equal(np.array(ep.crop((115,115,4211,4211))),np.array(piece))
 c=dict(prev['candidates'][i]) if i<2 else {'tile':tile,'size':[4096,4096],'finalPixelRectXYWH':[28672,28672,4096,4096],'worldRect':plan['sampleTile']['worldRect']}
 c.update({'file':str(cf),'sha256':sha(cf),'extendedContext':str(ef),'extendedContextSha256':sha(ef)});candidates.append(c)
rejoined=np.concatenate([np.array(Image.open(c['file'])) for c in candidates],axis=1);assert np.array_equal(rejoined,np.array(art));assert np.array_equal(rejoined[:,:4096],np.array(Image.open(prev['candidates'][0]['file'])))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);sheet=Image.new('RGB',(1240,1060),'white');draw=ImageDraw.Draw(sheet);draw.text((4,4),ap+' c07/c08 x8192 full seam; 1:1 segments 0..3',fill='black',font=font)
for seg in range(4):sheet.paste(art.crop((8192-150,seg*1024,8192+150,(seg+1)*1024)),(seg*310,36))
sheet.save(qa/'c07-c08-full-seam.png');sheet.save(qa/'c07-c08-full-seam.jpg',quality=94)
for y in (1024,2048,3072):art.crop((8192-450,y-450,8192+450,y+450)).save(qa/f'boundary-intersection-y{y}.png')
w(out/'assembly.json',{'appearance':ap,'status':'triple_pending_visual_review','priorPairV6':str(old),'priorPairV6Sha256':sha(old),'priorPairAssembly':str(P/ap/'pair_r08_c06_c07/output/pair-v6-assembly.json'),'newTileAssembly':str(t/'output/assembly.json'),'newTileAssemblySha256':sha(t/'output/assembly.json'),'triple':str(f),'tripleSha256':sha(f),'extendedContext':str(out/'extended-context.png'),'extendedContextSha256':sha(out/'extended-context.png'),'size':[12288,4096],'seamMetric':metric,'candidates':candidates,'splitPixelIdentityPassed':True,'c06PixelsUnchangedFromV6':True,'sourceResampling':False,'sourceUpscaledTo4K':False,'formalAcceptance':False,'wholeCityAccepted':False,'runtimePublished':False})
print(ap,'triple mechanically complete')