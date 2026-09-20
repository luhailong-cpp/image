from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util,sys
from datetime import datetime,timezone
PROD=Path(__file__).resolve().parent.parent
appearance=sys.argv[1];assert appearance in ('donghai_day','donghai_lantern')
root=PROD/appearance/'r08_c10'
left=PROD/appearance/'r08_c09'/('joined_pair' if appearance=='donghai_day' else 'joined_pair_v3')/'extended-context-pair.png'
right=root/'output/extended-context.png'
out=PROD/appearance/'r08_c08_c09_c10_joint/output_v1';qa=out/'qa'
if out.exists():raise RuntimeError('Version already exists; refusing overwrite')
qa.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('assembly',root/'assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=np.array(Image.open(left).convert('RGB'));b=np.array(Image.open(right).convert('RGB'))
assert a.shape==(4326,8422,3) and b.shape==(4326,4326,3)
pixels,metric=m.append_patch(a,b,m.load_seam_helper(),'c09_c10_full4096')
assert pixels.shape==(4326,12518,3)
im=Image.fromarray(pixels);core=im.crop((115,115,12403,4211));outputs=[]
def save(name,img,role,box=None):
 p=out/name;img.save(p,compress_level=4)
 e=dict(file=str(p),sha256=sha(p),pixels=list(img.size),role=role)
 if box:e['cropXYXY']=list(box)
 outputs.append(e)
save('extended-context-triple.png',im,'three_tiles_before_crop')
save('core12288x4096.png',core,'three_4k_core',(115,115,12403,4211))
for i,c in enumerate((8,9,10)):
 ident=f'r08_c{c:02d}';x=i*4096
 save(ident+'.png',core.crop((x,0,x+4096,4096)),'local_candidate',(x+115,115,x+4211,4211))
 save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'neighbor_context',(x,0,x+4326,4326))
joined=Image.new('RGB',(12288,4096))
for i,c in enumerate((8,9,10)):joined.paste(Image.open(out/f'r08_c{c:02d}.png'),(i*4096,0))
assert np.array_equal(np.array(joined),np.array(core))
assert np.array_equal(np.array(Image.open(out/'r08_c08.png')),np.array(Image.open(left.parent/'r08_c08.png')))
qaentries=[]
for x in (4096,8192):
 montage=Image.new('RGB',(1200,1024));boxes=[]
 for k in range(4):
  box=(x-150,k*1024,x+150,(k+1)*1024);montage.paste(core.crop(box),(k*300,0));boxes.append(list(box))
 p=qa/f'cross_x{x}_all4096_native.png';montage.save(p)
 qaentries.append(dict(path=str(p),sha256=sha(p),sourceBoxes=boxes,source='core12288x4096.png',resized=False,pixels=list(montage.size),panelOrder='top_to_bottom_shown_left_to_right'))
p=qa/'overview.jpg';core.resize((1536,512),Image.Resampling.LANCZOS).save(p,quality=90)
manifest=dict(status='candidate_pending_visual_QA_not_runtime_accepted',createdAtUtc=datetime.now(timezone.utc).isoformat(),appearance=appearance,accepted=False,runtimePublished=False,sources=[dict(path=str(p),sha256=sha(p)) for p in (left,right)],composition=dict(offsetXY=[8192,0],overlap=230,minimumErrorSeam=True,featherPixels=2,artResampling=False,artUpscaling=False,colorCorrection=False),seamMetric=metric,outputs=outputs,qa=qaentries,rejoinPixelIdentical=True,oldC08PixelUnchanged=True,scriptSha256=sha(__file__),scope='Only local c08,c09,c10 candidates, not entire city or formal acceptance')
(out/'assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(output=str(out),passed=True,rejoinPixelIdentical=True,oldC08PixelUnchanged=True)))
