from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib,importlib.util
from datetime import datetime,timezone
prod=Path(__file__).resolve().parent.parent
base=prod/'donghai_lantern/r08_c08_c09_c10_joint'; rep=base/'repairs_v2/fish_basin';out=base/'output_v2';qa=out/'qa'
assert not out.exists(),'Refusing overwrite'
qa.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('reg',prod/'tools/mechanical_join.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
src=base/'output_v1/extended-context-triple.png';original=np.array(Image.open(src).convert('RGB'));pixels=original.copy()
r=json.loads((rep/'native.record.json').read_text());patch=np.array(Image.open(r['outputPath']).convert('RGB'))
assert patch.shape==(1254,1254,3)
for k,h in [('outputPath','outputSha256'),('sourceOutputPath','sourceOutputSha256'),('promptPath','promptSha256')]: assert sha(r[k])==r[h]
for ref in r['actualInputReferences']:assert sha(ref['path'])==ref['sha256']
box=[v+115 for v in r['cropXYXY']];x0,y0,x1,y1=box;context=pixels[y0:y1,x0:x1].copy()
# Covers both defective blue fish with narrow original-context support, avoiding the wooden basin rim.
poly=[(0,210),(245,154),(472,154),(636,248),(761,376),(737,451),(806,661),(813,724),(772,782),(697,796),(705,938),(650,995),(501,1000),(413,948),(360,862),(288,770),(220,687),(168,593),(113,514),(59,389),(0,289)]
binary=np.zeros((1254,1254),np.uint8);cv2.fillPoly(binary,[np.array(poly,np.int32)],255)
dist=cv2.distanceTransform(binary,cv2.DIST_L2,5);weight=np.clip((dist-4)/24,0,1);weight=weight*weight*(3-2*weight);mask=np.rint(weight*255).astype(np.uint8)
result,flow,tone,report=reg.registered_join(context,patch,mask,max_shift=8,flow_inner=180,flow_full=64,tone_inner=180,tone_full=64,match_tone=True)
assert np.array_equal(result[mask==0],context[mask==0]);pixels[y0:y1,x0:x1]=result
assert np.array_equal(pixels[:y0],original[:y0]) and np.array_equal(pixels[y1:],original[y1:])
assert np.array_equal(pixels[y0:y1,:x0],original[y0:y1,:x0]) and np.array_equal(pixels[y0:y1,x1:],original[y0:y1,x1:])
Image.fromarray(mask).save(qa/'fish_roi_mask.png');Image.fromarray(result).save(qa/'fish_reconnected_native.png')
np.savez_compressed(out/'fish_registration_fields.npz',flow=flow,colorCorrection=tone)
im=Image.fromarray(pixels);core=im.crop((115,115,12403,4211));outputs=[];qaitems=[]
def save(name,img,role,box=None):
 p=out/name;img.save(p,compress_level=4);e=dict(file=str(p),sha256=sha(p),pixels=list(img.size),role=role)
 if box:e['cropXYXY']=list(box)
 outputs.append(e)
save('extended-context-triple.png',im,'native_joint_with_local_fish_repair')
save('core12288x4096.png',core,'three_4k_core',(115,115,12403,4211))
for i,c in enumerate((8,9,10)):
 x=i*4096;ident=f'r08_c{c:02d}'
 save(ident+'.png',core.crop((x,0,x+4096,4096)),'4096_candidate',(x+115,115,x+4211,4211))
 save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'neighbor_context',(x,0,x+4326,4326))
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r08_c{c:02d}.png')) for c in (8,9,10)],axis=1),np.array(core))
assert np.array_equal(np.array(Image.open(out/'r08_c08.png')),np.array(Image.open(base/'output_v1/r08_c08.png')))
def qsave(name,img,boxes,role):
 p=qa/name;img.save(p,compress_level=4);qaitems.append(dict(path=str(p),sha256=sha(p),pixels=list(img.size),sourceBoxes=boxes,resized=False,role=role))
for x in (4096,8192,9216,10240,11264):
 montage=Image.new('RGB',(1200,1024));boxes=[]
 for k in range(4):
  b=[x-150,k*1024,x+150,(k+1)*1024];montage.paste(core.crop(b),(k*300,0));boxes.append(b)
 qsave(f'v{x}_full_native.png',montage,boxes,'complete vertical seam 4096 pixels; panels left-to-right top-to-bottom')
for start,label,ys in [(8192,'c10',(1024,2048,3072)),(4096,'c09',(3072,))]:
 for y in ys:
  montage=Image.new('RGB',(1024,1200));boxes=[]
  for k in range(4):
   b=[start+k*1024,y-150,start+(k+1)*1024,y+150];montage.paste(core.crop(b),(0,k*300));boxes.append(b)
  qsave(f'h{y}_{label}_full_native.png',montage,boxes,'complete horizontal seam 4096 pixels; panels top-to-bottom left-to-right')
for x in (8192,9216,10240,11264):
 for y in (1024,2048,3072):
  b=[x-450,y-450,x+450,y+450];qsave(f'junction_x{x}_y{y}.png',core.crop(b),[b],'native intersection')
for label,b in [('top',[0,100,900,460]),('left',[0,300,470,1000]),('right',[460,240,960,1040]),('bottom',[230,700,900,1100])]:
 qsave(f'fish_roi_{label}_return.png',Image.fromarray(result).crop(b),[b],'actual curved ROI return edge in patch coordinate space')
core.resize((1536,512),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=92)
manifest=dict(status='candidate_pending_visual_reconnect_QA',appearance='donghai_lantern',accepted=False,runtimePublished=False,createdAtUtc=datetime.now(timezone.utc).isoformat(),source=dict(path=str(src),sha256=sha(src)),previousAssembly=dict(file=str(base/'output_v1/assembly.json'),sha256=sha(base/'output_v1/assembly.json')),nativeRepairRecords=[dict(file=str(rep/'native.record.json'),sha256=sha(rep/'native.record.json'))],registeredRepairs=[dict(id=r['id'],record=str(rep/'native.record.json'),recordSha256=sha(rep/'native.record.json'),boxXYXY=box,coordinateSpace='extended_triple',roiPolygonInPatch=poly,mechanical=report,maskPath=str(qa/'fish_roi_mask.png'),maskSha256=sha(qa/'fish_roi_mask.png'),registrationFieldPath=str(out/'fish_registration_fields.npz'),registrationFieldSha256=sha(out/'fish_registration_fields.npz'))],zeroMaskPixelsUnchanged=True,rejoinPixelIdentical=True,oldC08PixelUnchanged=True,outputs=outputs,qa=qaitems,composition=dict(nativePixelsRetained=True,sourceResampling='Limited subpixel registration at crop edges, max 8 px; fields retained',colorCorrection='Local edge correction up to 18 RGB, taper to zero at 180 px',artUpscaling=False),scriptSha256=sha(__file__))
(out/'assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(output=str(out),nativeRepairs=1,zeroMaskPixelsUnchanged=True,rejoinPixelIdentical=True,registration=report)))
