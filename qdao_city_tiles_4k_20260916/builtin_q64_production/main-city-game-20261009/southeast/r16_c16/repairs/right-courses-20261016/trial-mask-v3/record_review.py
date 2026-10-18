from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'refined-v1';R=D.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def wr(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
co=rd(O/'composition.json');op=co['operations'][0]
for e in [co['base'],co['baseContext'],co['core'],co['context'],op['source'],op['receipt'],op['alpha'],op['minimumErrorPaths']]:assert sha(e['path'])==e['sha256']
base=rgb(co['base']['path']);out=rgb(co['core']['path']);n=rgb(op['source']['path']);assert n.shape==(1254,1254,3)
a=np.array(Image.open(op['alpha']['path']));x0,y0,x1,y1=op['destinationCoreBox'];replay=base.copy()
for y,x in zip(*np.nonzero(a)):
 w=int(a[y,x])
 for c in range(3):replay[y0+y,x0+x,c]=(int(base[y0+y,x0+x,c])*(255-w)+int(n[y,x,c])*w+127)//255
assert np.array_equal(replay,out)
mask=np.zeros((4096,4096),bool);mask[y0:y1,x0:x1]=a>0
assert np.array_equal(out[~mask],base[~mask])
prior=rd(R/'trial-v2/composition.json');oldmask=np.array(Image.open(prior['operations'][0]['alpha']['path']))>0
assert not np.any((a>0)&~oldmask)
evidence=[]
notes={'upper-corner':'Upper side course meets the front projecting course. Mask returns to original corner post below the natural front and side dark edges; no orphan post end remains.','upper-joint':'New course transverse joint near local x800 ends in the course shadow; original wall vertical joint near x817 resumes at its underside. Prior separated blind ends removed.','upper-top-left':'Native wall texture and diagonal grouts cross top-left transition without a hard boundary.','upper-top-right':'Upper source transition continuous at wall divisions and fine stone grain.','upper-bottom-left':'Dark lower course edge preserved; original lower wall resumes without the earlier cutoff through the cap face.','upper-bottom-middle':'Bottom shadow contour continuous, original vertical wall joint meets underside, no short orphan protrusion.','upper-bottom-right':'Bottom transition near far-right wall joint continuous; no duplicate course or visible pasted boundary.','upper-left-boundary':'Front projecting cap, narrow corner return and lower post preserved across alpha boundary.','upper-right-map-border':'Side course continues to right map boundary; no terminal stripe introduced.'}
for e in co['evidence']:
 assert sha(e['path'])==e['sha256'];name=Path(e['path']).stem.replace('-100pct','')
 evidence.append(dict(**e,visuallyViewedAtNativeResolution=True,status='passed_local',finding=notes[name]))
qa=dict(schemaVersion=1,tile='r16_c16',reviewer='/root/assembly_resume',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),composition=ev(O/'composition.json'),core=co['core'],status='upper_local_pass_pending_root_review_lower_failed_not_adopted',upperStatus='passed_all_mask_edges_and_corner',evidence=evidence,overview=ev(O/'upper-composed-local-1254.png'),nativeArtworkGeneratedInThisSubtask=False,actualModel=None,outsideMaskExact=True,independentScalarPixelReplayExact=True,newMaskSupportSubsetOfPreviousAuthorizedUpperMask=True,lower=dict(status='failed_native_architecture_not_adopted',source=prior['operations'][1]['source'],receipt=prior['operations'][1]['receipt'],evidence=ev(D/'lower-corner-raw.png'),evidenceNativeCrop=[380,820,660,1160],description='Actual lower native has about50px height drop at corner: front cap top right around local(496,900), side cap top around(496,949). Mask selection cannot fill a correct joined contour from these pixels. Preserve original lower course pending repair; two AI attempts already done; no additional generation in this subtask.'),rejectedMaskVariant=dict(composition=ev(D/'composition.json'),reason='Approximate shadow line seed was above native bottom dark edge; resulting cut crossed cap face. Superseded by measured dark-line constrained mask.'),published=False,formalAccepted=False)
wr(O/'visual-qa.json',qa)
wr(D/'selected-operation-proposal.json',dict(schemaVersion=1,status=qa['status'],base=co['base'],operations=co['operations'],composition=ev(O/'composition.json'),visualQA=ev(O/'visual-qa.json'),core=co['core'],context=co['context'],lowerAdopted=False,formalAccepted=False,published=False))
print(json.dumps(dict(qa=ev(O/'visual-qa.json'),proposal=ev(D/'selected-operation-proposal.json'),composition=ev(O/'composition.json'),core=co['core'])))

