from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
R=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tianyong_festival')
P=R/'upperpair_r09_c07_c08_row10_c07_c10_20260918'; O=P/'output_v1';Q=P/'qa_v1';O.mkdir(parents=True,exist_ok=False);Q.mkdir()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('a',R/'r09_c08/assemble_resume_20260918.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
parents=[R/'L_r09_c07_r10_c07_c10/output_v3/vertical-extended-context.png',R/'L_r09_c07_r10_c07_c10/output_v3/row10-extended-context.png',R/'r09_c08/output_resume_20260918/extended-context.png']
oldv=np.array(Image.open(parents[0]).convert('RGB'));oldrow=np.array(Image.open(parents[1]).convert('RGB'));new=np.array(Image.open(parents[2]).convert('RGB'))
assert np.array_equal(oldv[4096:],oldrow[:,:4326])
top,hor=a.append_patch(oldv[:4326],new,a.load_seam_helper(),'r09_c07_c08')
joinedT,ver=a.append_patch(top.transpose(1,0,2),oldrow[:,:8422].transpose(1,0,2),a.load_seam_helper(),'r09_r10_c07_c08');quad=joinedT.transpose(1,0,2).copy()
row=oldrow.copy();row[:,:8422]=quad[4096:]
assert np.array_equal(row[230:],oldrow[230:]);assert np.array_equal(row[:,8422:],oldrow[:,8422:])
assert np.array_equal(quad[:,:4096],oldv[:,:4096])
Image.fromarray(quad).save(O/'quad-extended-context.png');Image.fromarray(row).save(O/'row10-extended-context.png')
qim=Image.fromarray(quad).crop((115,115,8307,8307));rim=Image.fromarray(row).crop((115,115,16499,4211));qim.save(O/'quad_8192_candidate.png');rim.save(O/'row10_16384_candidate.png')
files=[]
for r,c,im in [(9,c,qim.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8)]+[(10,c,rim.crop(((c-7)*4096,0,(c-6)*4096,4096))) for c in (7,8,9,10)]:
 f=O/f'r{r:02}_c{c:02}.png';im.save(f);files.append({'tile':f.stem,'path':str(f),'sha256':sha(f)})
assert np.array_equal(np.concatenate([np.array(Image.open(O/f'r10_c{c:02}.png')) for c in (7,8,9,10)],axis=1),np.array(rim))
assert np.array_equal(np.concatenate([np.concatenate([np.array(Image.open(O/f'r{r:02}_c{c:02}.png')) for c in (7,8)],axis=1) for r in (9,10)],axis=0),np.array(qim))
qim.resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'quad-overview.jpg',quality=90)
items=[]
for axis in ('vertical','horizontal'):
 for half in range(2):
  board=Image.new('RGB',(1280,1024) if axis=='vertical' else (1024,1280));boxes=[]
  for i in range(4):
   v=half*4096+i*1024;box=(3936,v,4256,v+1024) if axis=='vertical' else (v,3936,v+1024,4256)
   board.paste(qim.crop(box),(i*320,0) if axis=='vertical' else (0,i*320));boxes.append(box)
  f=Q/f'cross_{axis}_{half}.png';board.save(f);board.save(f.with_suffix('.jpg'),quality=95,subsampling=0);items.append({'file':str(f),'boxesLTRB':boxes,'pixelScale':1})
qim.crop((3469,3469,4723,4723)).save(Q/'fourway_1254.png');qim.crop((3469,3469,4723,4723)).save(Q/'fourway_1254.jpg',quality=95)
for x in (8192,12288):rim.crop((x-450,0,x+450,900)).save(Q/f'old_boundary_{x}_top.jpg',quality=95)
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'preliminary_joint_candidate_visual_defects_pending','parents':[{'path':str(f),'sha256':sha(f)} for f in parents],'files':files,'metrics':[hor,ver],'qa':items,'sourceResampling':False,'parentIncludesLimitedSeamRegistration':True,'exactTileRejoinVerified':True,'unchangedOutsideJoinPixelsVerified':True,'runtimePublished':False,'accepted':False,'knownInternalDefects':[{'tile':'r09_c08','nearXY':[1024,2820],'kind':'short_step_in_two_curved_stone_edges'},{'tile':'r09_c08','nearXY':[3140,560],'kind':'short_step_on_top_curved_stone_edge'}]}
(P/'assembly_v1.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({'directory':str(P),'files':len(files),'status':report['status']}))
