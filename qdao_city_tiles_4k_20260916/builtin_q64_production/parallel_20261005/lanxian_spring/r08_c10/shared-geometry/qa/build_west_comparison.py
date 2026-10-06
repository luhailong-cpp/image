from pathlib import Path
from PIL import Image
import json,hashlib,sys
import numpy as np
from datetime import datetime,timezone

B=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SPRING=B/'lanxian_spring'
DAY=B/'lanxian_day'
FILES={
 'springC09Core':SPRING/'r08_c09/repairs/join-endpoint/candidate_4096.png',
 'springC09Extended':SPRING/'r08_c09/repairs/join-endpoint/candidate_with_halo.png',
 'dayC10Core':DAY/'r08_c10/selected/core4096.png',
 'dayC10Extended':DAY/'r08_c10/selected/extended4326.png',
}
SOUTHWEST='--southwest' in sys.argv
if SOUTHWEST:
 OUT=OUT/'southwest'
 FILES['dayC10Core']=SPRING/'r08_c10/spring-edits/southwest/candidate_4096.png'
 FILES['dayC10Extended']=SPRING/'r08_c10/spring-edits/southwest/candidate_with_halo.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def item(p):
 with Image.open(p) as im:return {'file':str(p),'sha256':sha(p),'pixels':list(im.size)}

def main():
 OUT.mkdir(exist_ok=True,parents=True)
 imgs={k:Image.open(p).convert('RGB') for k,p in FILES.items()}
 if not SOUTHWEST:
  assert sha(FILES['dayC10Core'])=='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'
  assert sha(FILES['dayC10Extended'])=='2d4552bb7fa01baeb6fc0ac759360a50a08b9a90f65b285536a88947356e9e6e'
 a,z=imgs['springC09Core'],imgs['dayC10Core']
 ae,ze=imgs['springC09Extended'],imgs['dayC10Extended']
 assert a.size==z.size==(4096,4096)
 assert ae.size==ze.size==(4326,4326)
 outputs=[]
 for i in range(4):
  y=i*1024
  image=Image.new('RGB',(1024,1024));image.paste(a.crop((3584,y,4096,y+1024)),(0,0));image.paste(z.crop((0,y,512,y+1024)),(512,0))
  p=OUT/f'west-seam-{i+1:02d}-y{y:04d}-{y+1024:04d}.png';image.save(p)
  outputs.append({**item(p),'kind':'exact_core_join','localJoinX':512,'c10Y':[y,y+1024],'leftCropC09':[3584,y,4096,y+1024],'rightCropC10':[0,y,512,y+1024]})
  left=ae.crop((4096,y+115,4326,y+1139));right=ze.crop((0,y+115,230,y+1139))
  compare=Image.new('RGB',(460,1024));compare.paste(left,(0,0));compare.paste(right,(230,0))
  p=OUT/f'shared-overlap-{i+1:02d}-y{y:04d}-{y+1024:04d}.png';compare.save(p)
  diff=np.abs(np.asarray(left,dtype=np.float32)-np.asarray(right,dtype=np.float32))
  outputs.append({**item(p),'kind':'same_world_overlap_side_by_side','left':'spring c09','right':'spring c10 southwest edit' if SOUTHWEST else 'day c10','representedC10X':[-115,115],'c10Y':[y,y+1024],'meanAbsRGB':float(diff.mean()),'p95AbsRGB':float(np.quantile(diff,.95))})
 for name,y0 in [('north-corner',-115),('south-corner',3699)]:
  image=Image.new('RGB',(1024,512));image.paste(ae.crop((3699,y0+115,4211,y0+627)),(0,0));image.paste(ze.crop((115,y0+115,627,y0+627)),(512,0))
  p=OUT/f'{name}-with-halo.png';image.save(p)
  outputs.append({**item(p),'kind':'corner_with_halo','localJoinX':512,'c10Y':[y0,y0+512],'c10BoundaryY':115 if y0<0 else 397,'northSouthNeighborsAbsent':True})
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':{k:item(p) for k,p in FILES.items()},'operation':'QA only: exact 1:1 integer crop and paste; no resizing, blending or changes to candidates','coreMatchesExtended':{'springC09':np.array_equal(np.asarray(a),np.asarray(ae.crop((115,115,4211,4211)))),'dayC10':np.array_equal(np.asarray(z),np.asarray(ze.crop((115,115,4211,4211))))},'worldJoinX':36864,'worldYOrigin':28672,'outputs':outputs,'formalAccepted':False}
 report['variant']='spring c10 southwest edit over day shared geometry' if SOUTHWEST else 'day c10 qualified geometry'
 report['sourceKeyNote']='dayC10 keys contain the actual c10 comparison source named by their path; southwest mode substitutes the Spring Festival southwest edit.'
 write(OUT/'comparison-manifest.json',report)
 print(json.dumps({'sources':report['sources'],'outputs':len(outputs),'coreMatchesExtended':report['coreMatchesExtended']},ensure_ascii=False))

if __name__=='__main__':main()
