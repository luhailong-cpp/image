from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib,importlib.util
from datetime import datetime,timezone
prod=Path(__file__).resolve().parent.parent;base=prod/'donghai_day/r08_c08_c09_c10_joint';rep=base/'repairs_v1';out=base/'output_v2';qa=out/'qa'
if out.exists():raise RuntimeError('Refusing overwrite')
qa.mkdir(parents=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('reg',prod/'tools/mechanical_join.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
src=base/'output_v1/extended-context-triple.png';original=np.array(Image.open(src).convert('RGB'));pixels=original.copy();globalmask=np.zeros(pixels.shape[:2],np.uint8);reports=[]
polys={'fish_left':[(0,210),(250,165),(480,150),(770,200),(980,380),(1160,625),(1130,825),(980,890),(920,1010),(680,1020),(530,1040),(240,920),(50,530)],'fish_right':[(180,220),(450,200),(660,350),(905,650),(965,775),(825,905),(450,930),(275,740),(140,500)]}
for ident,poly in polys.items():
 d=rep/ident;r=json.loads((d/'native.record.json').read_text());patch=np.array(Image.open(r['outputPath']).convert('RGB'));assert patch.shape==(1254,1254,3)
 for k,h in [('outputPath','outputSha256'),('sourceOutputPath','sourceOutputSha256'),('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:assert sha(r[k])==r[h]
 box=[v+115 for v in r['cropXYXY']];x0,y0,x1,y1=box;context=pixels[y0:y1,x0:x1].copy()
 binary=np.zeros((1254,1254),np.uint8);cv2.fillPoly(binary,[np.array(poly,np.int32)],255)
 dist=cv2.distanceTransform(binary,cv2.DIST_L2,5);weight=np.clip((dist-4)/24,0,1);weight=weight*weight*(3-2*weight);mask=np.rint(weight*255).astype(np.uint8)
 result,flow,tone,report=reg.registered_join(context,patch,mask,max_shift=8,flow_inner=180,flow_full=64,tone_inner=180,tone_full=64,match_tone=True)
 assert np.array_equal(result[mask==0],context[mask==0]);pixels[y0:y1,x0:x1]=result;globalmask[y0:y1,x0:x1]|=mask
 for name,img in [('mask',Image.fromarray(mask)),('reconnected',Image.fromarray(result))]:img.save(qa/f'{ident}_{name}.png')
 np.savez_compressed(out/f'{ident}_registration_fields.npz',flow=flow,colorCorrection=tone)
 entries=[]
 for p in [qa/f'{ident}_mask.png',qa/f'{ident}_reconnected.png',out/f'{ident}_registration_fields.npz']:entries.append(dict(path=str(p),sha256=sha(p)))
 reports.append(dict(id=ident,record=str(d/'native.record.json'),recordSha256=sha(d/'native.record.json'),boxXYXY=box,coordinateSpace='extended_triple',roiPolygonInPatch=poly,mechanical=report,artifacts=entries))
assert np.array_equal(pixels[globalmask==0],original[globalmask==0])
im=Image.fromarray(pixels);core=im.crop((115,115,12403,4211));outputs=[]
def save(name,img,role,box=None):
 p=out/name;img.save(p,compress_level=4);e=dict(file=str(p),sha256=sha(p),pixels=list(img.size),role=role)
 if box:e['cropXYXY']=list(box)
 outputs.append(e)
save('extended-context-triple.png',im,'native_joint_with_two_local_fish_repairs')
save('core12288x4096.png',core,'three_4k_core',(115,115,12403,4211))
for i,c in enumerate((8,9,10)):
 x=i*4096;ident=f'r08_c{c:02d}'
 save(ident+'.png',core.crop((x,0,x+4096,4096)),'4096_candidate',(x+115,115,x+4211,4211));save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'neighbor_context',(x,0,x+4326,4326))
joined=Image.new('RGB',(12288,4096))
for i,c in enumerate((8,9,10)):joined.paste(Image.open(out/f'r08_c{c:02d}.png'),(i*4096,0))
assert np.array_equal(np.array(joined),np.array(core));assert np.array_equal(np.array(Image.open(out/'r08_c08.png')),np.array(Image.open(base/'output_v1/r08_c08.png')))
qaitems=[]
for x in (4096,8192,8192+1024,8192+2048,8192+3072):
 montage=Image.new('RGB',(1200,1024));boxes=[]
 for k in range(4):
  box=(x-150,k*1024,x+150,(k+1)*1024);montage.paste(core.crop(box),(k*300,0));boxes.append(list(box))
 p=qa/f'v{x}_full_native.png';montage.save(p);qaitems.append(dict(path=str(p),sha256=sha(p),boxes=boxes,resized=False))
for y in (1024,2048,3072):
 montage=Image.new('RGB',(1024,1200));boxes=[]
 for k in range(4):
  box=(8192+k*1024,y-150,8192+(k+1)*1024,y+150);montage.paste(core.crop(box),(0,k*300));boxes.append(list(box))
 p=qa/f'h{y}_c10_full_native.png';montage.save(p);qaitems.append(dict(path=str(p),sha256=sha(p),boxes=boxes,resized=False))
for y in (1024,2048,3072):
 for x in (8192,9216,10240,11264):
  p=qa/f'junction_x{x}_y{y}.png';core.crop((x-200,y-200,x+200,y+200)).save(p)
core.resize((1536,512),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=90)
manifest=dict(status='candidate_pending_repair_reconnect_visual_QA',appearance='donghai_day',accepted=False,runtimePublished=False,createdAtUtc=datetime.now(timezone.utc).isoformat(),source=dict(path=str(src),sha256=sha(src)),nativeRepairRecords=[dict(file=e['record'],sha256=e['recordSha256']) for e in reports],registeredRepairs=reports,zeroMaskPixelsUnchanged=True,rejoinPixelIdentical=True,oldC08PixelUnchanged=True,outputs=outputs,qa=qaitems,composition=dict(nativePixelsRetained=True,sourceResampling='Limited subpixel registration at local repair borders, max8px; disclosed fields retained',colorCorrection='Local edge correction up to18RGB, taper to zero at180px',artUpscaling=False),scriptSha256=sha(__file__))
(out/'assembly.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(output=str(out),nativeRepairs=len(reports),zeroMaskPixelsUnchanged=True,rejoinPixelIdentical=True)))
