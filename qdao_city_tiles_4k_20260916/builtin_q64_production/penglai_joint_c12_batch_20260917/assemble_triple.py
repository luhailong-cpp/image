import argparse,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
BASE=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('appearance');a=ap.parse_args()
 city=BASE/a.appearance;root=city/'r09_c10_c11_c12_joint';out=root/'output';qa=root/'qa'
 out.mkdir(parents=True,exist_ok=True);qa.mkdir(exist_ok=True)
 oldout=city/'r09_c10_c11_joint'/'output'
 if a.appearance=='penglai_mid_autumn':oldout=oldout/'v3'
 left=oldout/'extended-context.png';right=city/'r09_c12'/'output'/'extended-context.png'
 spec=importlib.util.spec_from_file_location('assembly',city/'r09_c12'/'assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 l=np.array(Image.open(left).convert('RGB'));r=np.array(Image.open(right).convert('RGB'))
 assert l.shape==(4326,8422,3) and r.shape==(4326,4326,3)
 ext,metric=m.append_patch(l,r,m.load_seam_helper(),'r09_c11_c12')
 assert ext.shape==(4326,12518,3) and np.array_equal(ext[:,:8192],l[:,:8192]) and np.array_equal(ext[:,8422:],r[:,230:])
 full=Image.fromarray(ext);triple=full.crop((115,115,12403,4211));files=[]
 def save(im,p):
  im.save(p);files.append({'file':p.relative_to(root).as_posix(),'pixels':list(im.size),'sha256':sha(p)})
 save(full,out/'extended-context.png');save(triple,out/'triple-12288x4096.png')
 for col in range(3):save(triple.crop((4096*col,0,4096*(col+1),4096)),out/f'{a.appearance}_r09_c{10+col:02d}_4k_joint_candidate.png')
 for col in range(3):assert np.array_equal(np.array(Image.open(out/f'{a.appearance}_r09_c{10+col:02d}_4k_joint_candidate.png')),np.array(triple.crop((4096*col,0,4096*(col+1),4096))))
 triple.resize((2048,683),Image.Resampling.LANCZOS).save(qa/'overview.jpg',quality=90)
 for y in [0,1024,2048,2842]:triple.crop((7565,y,8819,y+1254)).save(qa/f'boundary_y{y:04d}.jpg',quality=93)
 rt=triple.crop((8192,0,12288,4096))
 for axis in ('x','y'):
  for pos in (1024,2048,3072):
   strip=rt.crop((pos-150,0,pos+150,4096)) if axis=='x' else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
   sheet=Image.new('RGB',(1200,1024))
   for k in range(4):sheet.paste(strip.crop((0,1024*k,300,1024*(k+1))),(k*300,0))
   sheet.save(qa/f'internal_{axis}{pos}.jpg',quality=93)
 inputs=[]
 for p in [left,right]:
  assembly=p.parent/'assembly.json'; assert assembly.exists(),assembly
  inputs.append({'contextPath':str(p),'contextSha256':sha(p),'assemblyPath':str(assembly),'assemblySha256':sha(assembly)})
 rec={'schemaVersion':1,'appearance':a.appearance,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA_not_published','runtimePublished':False,'formallyAccepted':False,'sources':inputs,'scriptPath':str(Path(__file__).resolve()),'scriptSha256':sha(__file__),'geometry':{'joinedPixels':[12518,4326],'cropLTRB':[115,115,12403,4211],'triplePixels':[12288,4096],'tilePixels':[4096,4096],'overlap':230,'globalPixelRectXYWH':[36864,32768,12288,4096]},'method':'minimum error native overlap seam, 2px feather then exact split','jointStageResampling':False,'sourceArtUpscaled':False,'upstreamProcessing':'Preserved previous pair local native repairs and limited registration; see parent manifests','unchangedOutsideOverlap':True,'splitPixelIdentity':True,'seamMetric':metric,'outputs':files,'qa':{'overview':'qa/overview.jpg','fullInternalLines':['qa/'+p.name for p in qa.glob('internal*.jpg')],'fullSharedBoundary':['qa/'+p.name for p in qa.glob('boundary*.jpg')],'visualStatus':'pending','externalNeighbors':'unverified','runtimeAccepted':False}}
 (out/'assembly.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'appearance':a.appearance,'joint':str(root),'splitIdentity':True}))
if __name__=='__main__':main()
