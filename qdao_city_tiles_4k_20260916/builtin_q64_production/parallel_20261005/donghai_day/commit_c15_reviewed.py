"""Publish the frozen, independently reviewed c15 candidate as current output."""
from pathlib import Path
import json,hashlib,shutil,os
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/approved-integration';O=T/'output'
EXPECTED='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585';BASE='41cd6b8daffcee9e67069688f5b3d5150fbf7576975545ee2287cac44201f50b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'file':str(p),'sha256':sha(p)}
def js(p,v):
 temp=Path(str(p)+'.pending');temp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p)
def cp(a,b):
 temp=Path(str(b)+'.pending');shutil.copyfile(a,temp);assert sha(a)==sha(temp);os.replace(temp,b)
candidate=D/'candidate.png';extended=D/'extended-context.png';assert sha(candidate)==EXPECTED and sha(O/'r08_c15.png')==BASE
m=load(D/'manifest.json');assert sha(extended)==m['extendedContext']['sha256'];reviews=[]
for n,group in [('insertion-review','views'),('independent-internal-review','items'),('root-external-review','sheets')]:
 p=D/(n+'.json');r=load(p);assert r['candidateSha256']==EXPECTED and r['result'].startswith('pass')
 for item in r[group]:
  filename=item.get('file',item.get('path'));assert sha(filename)==item.get('reviewedSha256',item['sha256'])
 reviews.append(ref(p))
review={'candidateSha256':EXPECTED,'result':'pass','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'20 native insertion views; 6 native full internal seams; 9 native crossings; native 4 corners and full west edge; overview','reports':reviews,'formalAccepted':False,'wholeCityComplete':False}
js(D/'review.json',review)
m['visualReview']='passed actual insertion, independent internal, and independent outer QA';m['reviewReports']=reviews
for item in m['insertionQA']:item['visualInspection']='actually viewed at native scale; pass'
m['commitTool']=ref(Path(__file__));js(D/'manifest.json',m)
oldpath=O/'assembly-manifest.json';old=load(oldpath);assert old['output']['sha256']==BASE
history=D/'previous-assembly-manifest.json';assert not history.exists();shutil.copyfile(oldpath,history)
prior=dict(old['output'],availability='superseded',historicalRecord=ref(history),pixelValidation='native source crop RGB hashes validated before integration')
cp(candidate,O/'r08_c15.png');cp(extended,O/'extended-context.png')
output=dict(ref(O/'r08_c15.png'),pixels=[4096,4096]);ex=dict(ref(O/'extended-context.png'),pixels=[4326,4326]);assert output['sha256']==EXPECTED
chain={'operation':'native material/water seam repairs, bounded local insertion RGB drift matching, and structural east-edge/115px halo correction without resampling','priorOutput':prior,'integrationManifest':ref(D/'manifest.json'),'review':ref(D/'review.json'),'output':output,'extendedContext':ex,'eastBoundaryCorrection':m['eastBoundaryCorrection']}
old.setdefault('postprocessingChain',[]).append(chain);old.update(output=output,extendedContext=ex,status='complete-pixel-candidate-repaired-reviewed',postprocessingProtected=True,qa=m['qa'],actualVisualReview=ref(D/'review.json'),formalAccepted=False)
old.setdefault('qaCoverage',{})['inspectionStatus']='actual insertion, internal, intersections, corners and common west edge reviewed and passed'
js(oldpath,old);js(O/'r08_c15.png.generation.json',dict(output,operation='native patch assembly with recorded seam postprocessing',assemblyManifest=ref(oldpath),postprocessingChain=old['postprocessingChain'],actualModel=None,actualQuality=None,formalAccepted=False))
assert sha(O/'r08_c15.png')==EXPECTED and sha(O/'extended-context.png')==ex['sha256']
print(json.dumps({'output':output,'extendedContext':ex,'review':ref(D/'review.json'),'postprocessingProtected':True}))
