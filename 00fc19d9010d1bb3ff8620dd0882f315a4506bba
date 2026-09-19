import json,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');A=B/'penglai_joint_c12_batch_20260917/audit_20260918';J=B/'penglai_day/r09_c10_c11_c12_joint';O=J/'output_v2_20260918';Q=J/'qa_v2_20260918';assert not O.exists();O.mkdir();Q.mkdir()
sp=importlib.util.spec_from_file_location('mj',B/'tools/mechanical_join.py');mj=importlib.util.module_from_spec(sp);sp.loader.exec_module(mj)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=np.array(Image.open(J/'output/triple-12288x4096.png').convert('RGB'));canvas=old.copy();records=[];changedmask=np.zeros(old.shape[:2],bool)
queue=json.loads((A/'day-repair-queue.json').read_text())['jobs']
for j in queue:
 native=A/'repairs/native'/(j['id']+'.png');rec=native.with_suffix('.record.json');patch=np.array(Image.open(native).convert('RGB'));bx,by,ex,ey=j['sourceCropLTRB'];rx,ry,rex,rey=j['proposedPasteROIInTriple']
 sx=max(bx,rx-64);sex=min(ex,rex+64);sy=by;sey=ey
 context=canvas[sy:sey,sx:sex].copy();p=patch[sy-by:sey-by,sx-bx:sex-bx].copy();h,w=context.shape[:2]
 yy,xx=np.mgrid[:h,:w];gx=xx+sx;gy=yy+sy
 distance=np.minimum.reduce([gx-rx,rex-1-gx,gy-ry,rey-1-gy]).astype(float)
 # Feather only within 20px of the selected ROI; preserve all zero-mask samples.
 alpha=np.clip(distance/20,0,1);alpha=alpha*alpha*(3-2*alpha);mask=np.uint8(np.rint(alpha*255))
 merged,flow,corr,report=mj.registered_join(context,p,mask,max_shift=8,flow_inner=150,flow_full=60,tone_inner=150,tone_full=60)
 canvas[sy:sey,sx:sex]=merged;changedmask[sy:sey,sx:sex]|=mask>0
 mp=O/(j['id']+'.mask.png');Image.fromarray(mask).save(mp);fp=O/(j['id']+'.flow.npy');np.save(fp,flow);cp=O/(j['id']+'.color-correction.npy');np.save(cp,corr)
 Image.fromarray(merged).save(Q/(j['id']+'.joined-support.png'))
 records.append({'id':j['id'],'nativeSource':str(native),'nativeSha256':sha(native),'record':str(rec),'recordSha256':sha(rec),'sourceCropLTRB':j['sourceCropLTRB'],'pasteROIInTriple':j['proposedPasteROIInTriple'],'registrationSupportLTRB':[sx,sy,sex,sey],'mask':{'path':str(mp),'sha256':sha(mp)},'flow':{'path':str(fp),'sha256':sha(fp)},'colorCorrection':{'path':str(cp),'sha256':sha(cp)},'joinReport':report})
assert np.array_equal(canvas[~changedmask],old[~changedmask]);assert np.array_equal(canvas[:,:4096],old[:,:4096])
im=Image.fromarray(canvas);im.save(O/'triple-12288x4096.png');ext=np.array(Image.open(J/'output/extended-context.png').convert('RGB'));ext[115:4211,115:12403]=canvas;Image.fromarray(ext).save(O/'extended-context.png')
files=[]
for k in range(3):
 p=O/f'penglai_day_r09_c{k+10}_4k_joint_candidate_v2.png';im.crop((4096*k,0,4096*(k+1),4096)).save(p);assert np.array_equal(np.array(Image.open(p)),canvas[:,4096*k:4096*(k+1)]);files.append({'file':str(p),'pixels':[4096,4096],'sha256':sha(p),'tile':f'r09_c{k+10}'})
rt=im.crop((8192,0,12288,4096))
for axis in ('x','y'):
 for pos in (1024,2048,3072):
  strip=rt.crop((pos-150,0,pos+150,4096)) if axis=='x' else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
  sheet=Image.new('RGB',(1200,1024))
  for k in range(4):sheet.paste(strip.crop((0,k*1024,300,(k+1)*1024)),(k*300,0))
  sheet.save(Q/f'internal_{axis}{pos}.png')
for y in [0,1024,2048,2842]:im.crop((7565,y,8819,y+1254)).save(Q/f'boundary_y{y:04d}.png')
for y in [1024,2048,3072]:
 sheet=Image.new('RGB',(1200,400))
 for k,x in enumerate([1024,2048,3072]):sheet.paste(rt.crop((x-200,y-200,x+200,y+200)),(k*400,0))
 sheet.save(Q/f'intersections_y{y}.png')
im.crop((7940,2900,8520,3380)).save(Q/'repair-overlap-crossing.png')
im.resize((2048,683)).save(Q/'overview.jpg',quality=92)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'penglai_day','status':'candidate_pending_visual_QA_not_published','runtimePublished':False,'formallyAccepted':False,'parentAssembly':str(J/'output/assembly.json'),'parentAssemblySha256':sha(J/'output/assembly.json'),'parentTripleSha256':sha(J/'output/triple-12288x4096.png'),'scriptPath':str(Path(__file__)),'scriptSha256':sha(Path(__file__)),'repairs':records,'sourceArtUpscaled':False,'sourceResampling':'Limited optical registration of native repair edge support, maximum 8 pixels; full fields recorded.','zeroMaskPixelsUnchanged':True,'unchangedC10':True,'splitPixelIdentity':True,'externalNeighbors':'unverified','outputs':files,'triple':{'path':str(O/'triple-12288x4096.png'),'sha256':sha(O/'triple-12288x4096.png')},'extendedContext':{'path':str(O/'extended-context.png'),'sha256':sha(O/'extended-context.png')},'visualQa':'pending'}
(O/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'output':str(O),'qa':str(Q),'repairs':len(records),'outsideUnchanged':True}))