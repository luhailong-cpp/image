from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,numpy as np
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');D=P/'lanxian_day/r08_c09'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
p=j(D/'plan.json');src=D/'regional-reference/regional-v1.png';assert not list((D/'guides').glob('*.png'))
canvas=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC)
left=Image.open(p['leftNeighborBoundary']['file']).convert('RGB')
# Generated regional reference is for layout only; actual selected native west halo constrains guides.
unconstrained=canvas.copy();canvas.paste(left.crop((4096,0,4211,4326)),(0,0))
mother=D/'guides/layout-canvas-only.png';canvas.save(mother)
preview=Image.new('RGB',(2420,1254),'white');preview.paste(left.resize((1254,1254),Image.Resampling.LANCZOS),(0,0));preview.paste(canvas.resize((1254,1254),Image.Resampling.LANCZOS),(1187,0));preview.save(D/'regional-reference/c08-c09-calibrated-layout-preview.png')
sheet=Image.new('RGB',(1240,1060),'white');ImageDraw.Draw(sheet).text((4,4),'Regional layout seam diagnostic only; native west vs upscaled new guide; not final art',fill='black')
seam=Image.new('RGB',(460,4096));seam.paste(left.crop((3981,115,4211,4211)),(0,0));seam.paste(unconstrained.crop((115,115,345,4211)),(230,0))
for seg in range(4):sheet.paste(seam.crop((80,seg*1024,380,(seg+1)*1024)),(seg*310,36))
sheet.save(D/'regional-reference/c08-c09-guide-boundary-diagnostic.png')
patches=[];arrays={}
for r in range(4):
 for c in range(4):
  ident=f'r{r+1:02d}_c{c+1:02d}';box=[c*1024,r*1024,c*1024+1254,r*1024+1254];g=canvas.crop(box);f=D/'guides'/f'{ident}.layout-only.png';g.save(f);arrays[r,c]=np.asarray(g)
  patches.append({'id':ident,'row':r+1,'column':c+1,'fullCanvasBox':box,'guide':str(f),'guideSha256':sha(f),'guideOnly':True})
checks=0
for r in range(4):
 for c in range(4):
  if c<3:assert np.array_equal(arrays[r,c][:,-230:],arrays[r,c+1][:,:230]);checks+=1
  if r<3:assert np.array_equal(arrays[r,c][-230:],arrays[r+1,c][:230]);checks+=1
shutil.copy2(D/'plan.json',D/'plan.before-guides-20260921.json')
p.update(status='sixteen_native_details_pending_regional_visual_gate',patches=patches)
p['guidePreparation']={'status':'ready_unified_style_reference','guideOnly':True,'motherSource':str(src),'motherSha256':sha(src),'motherPixels':[1254,1254],'mother':str(mother),'motherSha256':sha(mother),'canvasPixels':[4326,4326],'method':'regional reference resampled for guides only; exact115px west native core imposed','sharedOverlapChecks':checks,'allSharedOverlapPixelsIdentical':True,'finalArtResampling':False}
(D/'plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Clone established assembler with corrected tile and transparent configured target metadata.
code=(P/'lanxian_day/r08_c08/assemble_builtin_single_v1.py').read_text(encoding='utf-8-sig').replace('r08_c08','r08_c09').replace('GPT Image 2.0 (host builtin)','ChatGPT Images 2.5 target; host managed; actual variant unverified')
code=code.replace('def assemble() -> dict:\n','def assemble() -> dict:\n    assert not MANIFEST.exists(), "Preserve existing assembly version"\n')
(D/'assemble_builtin_single_v1.py').write_text(code,encoding='utf-8')
print('Day16 guides prepared;24 shared overlaps identical. Regional seam diagnostic awaits visual check before native detail generation.')
