from workflow import *
from PIL import Image
import numpy as np

# Adopt only the fully reviewed water candidate; retain all other completed files as pending.
q=ROOT/'qa/r14_c13-right-full-20261016-v03';wr=read(q/'actual-review.json');proof=read(q/'source-proof.json')
assert sha(Path(wr['candidate']))==wr['candidateSha256']==proof['candidateSha256']
assert proof['sourceReplayMismatch']==0 and proof['coveredPixels']==16777216
for s in proof['sources']:assert sha(Path(s['file']))==s['sha256']
review={'tile':'r14_c13','candidate':wr['candidate'],'candidateSha256':wr['candidateSha256'],'internalPassed':True,'externalPassed':False,'formalAccepted':False,'sourceProof':str(q/'source-proof.json'),'reviewedAt':now(),'workerReview':str(q/'actual-review.json'),'rootViewed':['preview','h13','h22','h32','v22','v23','v32','v33','junction_22','junction_32','overlay-19-left','overlay-19-right','overlay-19-top','overlay-19-bottom'],'otherEvidence':'Worker actual visual inspection and unchanged hash reuse accepted; no need to rescan unchanged historical candidates.','pending':'Actual neighboring edges and four-tile corners; north r13_c13 remains unpassed.'}
write(q/'root-internal-review-20261016.json',review)
r=read(ROOT/'production-resume-20261012.json')
for tid,rev in [('r08_c13','root-full-20261016-v01'),('r09_c10','wall-oct16-v01'),('r13_c10','left-oct16-v01'),('r13_c14','right-full-20261016-v01')]:
 f=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';assert f.exists()
 ent={'tile':tid,'candidate':str(f),'sha256':sha(f),'fullyCovered':True,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'status':'full_candidate_pending_root_review_or_local_repair'}
 r['pendingCandidates']=[x for x in r['pendingCandidates'] if x['tile']!=tid]+[ent]
old=next(x for x in r['currentAdoptedCandidates'] if x['tile']=='r08_c12')
r['currentAdoptedCandidates']=[x for x in r['currentAdoptedCandidates'] if x['tile']!='r08_c12']
old.update(internalPassed=False,externalPassed=False,localArtworkAcceptanceReady=False,status='reopened_confirmed_leaf_cut',pending='Hard vertical foliage cut at tile x3981,y3072..3584, confirmed in actual adjacent strip; native local repair pending.',reviewEvidence=str(ROOT/'qa/r08_c13-start-20261013/p41-W.png'))
r['pendingCandidates']=[x for x in r['pendingCandidates'] if x['tile']!='r08_c12']+[old]
write(ROOT/'production-resume-20261012.json',r)

def request(name,tid,origin,target,parts,prompt):
 g=ROOT/'guides'/f'{name}.target.png';assert not g.exists();target.save(g)
 write(Path(str(g)+'.generation.json'),{'tile':tid,'tileRelativeOrigin':origin,'dimensions':[1254,1254],'operation':'exact crop and paste of current actual selected native pixels; reference only','parts':parts,'usableAsFinalArt':False})
 pf=ROOT/'prompts'/f'{name}.prompt.txt';pf.write_text(prompt,encoding='utf-8')
 refs=[{'file':str(g),'sha256':sha(g),'role':'registered native edit target with current actual neighboring pixels'}]
 write(ROOT/'prompts'/f'{name}.request.json',{'tile':tid,'tileRelativeOrigin':origin,'promptPath':str(pf),'references':refs})
 write(ROOT/'prompts'/f'{name}.args.json',{'prompt':prompt,'referenced_image_paths':[str(g)],'transparent_background':False})
 print(g)

f=ROOT/'tiles/r08_c13.candidate-root-full-20261016-v01.png';box=[397,1421,1651,2675]
request('r08_c13_pillar_joint_whole_v01','r08_c13',box[:2],Image.open(f).convert('RGB').crop(box),[{'file':str(f),'sha256':sha(f),'sourceCrop':box,'destination':[0,0]}],
 'Use case: precise-object-edit. Edit this exact 1254x1254 native stone pillar crop. Repair only the visibly broken pillar shaft across the horizontal line at y627: the upper shaft and its front relief are shifted sideways relative to the lower shaft. Reconstruct ONE coherent upright ivory stone pillar, with continuous straight shaft edges, one consistent front plane and one coherent recessed floral relief frame. Correct the impossible step and interrupted carving at that line. Preserve the existing cap and base scale, balustrade slope and connections, all surrounding flowers, leaves and grey paving. Keep the outermost 100 pixels fixed exactly and keep the crop framing, daylight and hand-painted Q Daoist style. No new post, double shaft, extra cap, bands, objects, text or blur. Render one opaque native 1254x1254 image with crisp original painted detail. This is a local geometric repair, not a redesigned scene.')

tid='r08_c12';target=Image.new('RGB',(1254,1254));cover=np.zeros((1254,1254),dtype=np.uint8);parts=[]
def paste(file,crop,dest):
 f=ROOT/file;im=Image.open(f).convert('RGB').crop(crop);x,y=dest;target.paste(im,tuple(dest));cover[y:y+im.height,x:x+im.width]+=1;parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest})
paste('tiles/r08_c12.candidate-v15.png',[2957,2957,4096,4096],[0,0])
paste('native/r08_c13_p31_v01.png',[115,1024,230,1139],[1139,0])
paste('native/r08_c13_p41_v01.png',[115,115,230,1139],[1139,115])
paste('tiles/r09_c12.candidate-v09.png',[2957,0,4096,115],[0,1139])
paste('tiles/r09_c13.candidate-v02.png',[0,0,115,115],[1139,1139])
assert np.all(cover==1)
request('r08_c12_foliage_whole_v01',tid,[2957,2957],target,parts,
 'Use case: precise-object-edit. Edit this exact native 1254x1254 painted foliage crop. Remove ONLY the artificial vertical rectangular cut at x1024, mainly y115 to y650: existing green leaves are sliced into a straight edge by an old pasted guide. Restore their natural full pointed leaf silhouettes and connected branches through this line. Match the same existing foliage, flowers, rocks, colors, light and shadows, preserving their positions and identities. Keep the outermost 100-pixel border exactly fixed so this crop joins the actual neighbors; keep the rest of the image unchanged except the narrow area needed to heal the clipped leaves. Do not add objects, new flower groups, paving, text or new branches unrelated to the existing plants. No blur, guide rectangles or geometric edges in foliage. One opaque native 1254x1254 result, crisp painted Q Daoist game-map detail, same framing.')
