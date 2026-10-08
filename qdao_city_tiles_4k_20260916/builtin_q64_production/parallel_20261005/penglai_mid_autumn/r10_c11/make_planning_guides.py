"""Create planning-only 4326 canvas, 16 guides and explicitly non-final QA; no AI."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
F=Path(__file__).resolve().parent;ROOT=F.parent
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now,deriv
sys.path.insert(0,str(ROOT/'tools/multi_edge'))
import cli,engine
R=F/'references';G=F/'guides';Q=F/'qa'
def ref(p):return dict(file=str(p),sha256=sha(p))
_,plan,wave,neighbors=cli.setup('r10_c11')
S=R/'structure.png';D=Path(plan['sharedDayStructure']['file'])
assert sha(S)=='13bea637250fe19c43c1c090204e77870911fe5176a5d9d2f9d6624fe8a780d1'
assert sha(D)==plan['sharedDayStructure']['sha256']
assert not (R/'planning-extended4326.png').exists() and not (G/'index.json').exists()
G.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
night=Image.open(S).convert('RGB');day=Image.open(D).convert('RGB')
assert night.size==day.size==(1254,1254)
big=night.resize((4326,4326),Image.Resampling.LANCZOS)
P=R/'planning-extended4326.png';big.save(P)
deriv(P,[S],dict(kind='planning_only_upscale_no_native_production_pixels',sourcePixels=[1254,1254],outputPixels=[4326,4326],globalRectXYWH=plan['referenceFrameGlobalXYWH'],resampling='LANCZOS',nativeProductionPixelCount=0))
guides=[]
for row in range(4):
 for col in range(4):
  p=G/f'p{row+1}{col+1}.png';b=[col*1024,row*1024,col*1024+1254,row*1024+1254]
  big.crop(b).save(p)
  deriv(p,[P,S],dict(kind='exact_crop_of_planning_only_canvas_not_final_native_detail',cropLTRB=b,globalRectXYWH=[40845+col*1024,36749+row*1024,1254,1254],core=1024,halo=115,overlap=230,sourcePlanningEnlargement=4326/1254,nativeProductionPixelCount=0))
  guides.append(dict(id=p.stem,**ref(p),cropLTRB=b,globalPatchXYWH=[40845+col*1024,36749+row*1024,1254,1254],productionPixels=False))
# Shared overlaps must be identical crops of one canvas.
for row in range(4):
 for col in range(4):
  a=np.array(Image.open(G/f'p{row+1}{col+1}.png'))
  if col<3:assert np.array_equal(a[:,1024:],np.array(Image.open(G/f'p{row+1}{col+2}.png'))[:,:230])
  if row<3:assert np.array_equal(a[1024:],np.array(Image.open(G/f'p{row+2}{col+1}.png'))[:230])
write(G/'index.json',dict(createdAt=now(),planningSource=ref(P),nightStructure=ref(S),wavefront='NE',core=1024,halo=115,overlap=230,guidePixels=[1254,1254],guideOverlapsPixelIdentical=True,guideCount=16,guides=guides,productionPixels=False,nativeProductionPixelCount=0))
core=big.crop((115,115,4211,4211))
neighborims={role:Image.fromarray(n['pixels']) for role,n in neighbors.items()}
qa=[]
for name,image,op,roles in engine.qa_images(core,neighborims,'NE'):
 if name not in ['north-shared-full','east-shared-full','four-tile-northeast-corner']:continue
 p=Q/('planning-'+name+'.png');image.save(p)
 sources=[P if role=='current' else neighbors[role]['path'] for role in roles]
 operation=dict(kind='planning_only_join_review_not_final_seam_acceptance',helperOperation=op,helperSourceRoles=roles,planningSourceCropLTRB=[115,115,4211,4211],planningEnlargement=4326/1254,actualNeighborScale=1,outputDisplayScale=1,finalNativeSeamVerified=False)
 deriv(p,sources,operation);qa.append(dict(**ref(p),operation=operation,actuallyViewed=False))
for i,(x0,y0) in enumerate([(0,0),(627,0),(0,627),(627,627)],1):
 b=[x0,y0,x0+627,y0+627]
 im=Image.new('RGB',(1254,627));im.paste(day.crop(b),(0,0));im.paste(night.crop(b),(627,0))
 p=Q/f'day-night-quadrant{i}.png';im.save(p)
 op=dict(kind='same_coordinate_day_left_night_right_planning_quadrants',sourceCropLTRB=b,sourceScale=1,productionPixels=False)
 deriv(p,[D,S],op);qa.append(dict(**ref(p),operation=op,actuallyViewed=False))
write(Q/'structure-review-index.json',dict(createdAt=now(),tile='r10_c11',structure=ref(S),planningSource=ref(P),guides=ref(G/'index.json'),items=qa,productionPixels=False,rootReviewPending=True,formalAccepted=False))
gen=read(str(S)+'.generation.json');req=read(F/'night-structure.request.json');call=read(F/'night-structure.call.json')
assert gen['submittedParameters']==req['submittedParameters']
assert call=={k:v for k,v in gen['submittedParameters'].items() if k not in ['model','quality']}
assert sha(gen['evidence']['sourceOutputPath'])==gen['sha256']
write(F/'night-structure.submission-completion.json',dict(recordedAt=now(),status='builtin_generation_completed_saved',generationCompletionRecordedAt=gen['generatedAt'],submissionStartedAt=None,submissionStartedAtReason='Tool service start timestamp unavailable in this agent record; no guessed timestamp.',preparedRequestHistorical=ref(F/'night-structure.request.json'),exactCall=ref(F/'night-structure.call.json'),actualSubmittedParameters=gen['submittedParameters'],sourceResult=gen['evidence'],savedOutput=ref(S),savedGenerationRecord=ref(Path(str(S)+'.generation.json')),configTarget=gen['configSnapshot'],actualModel=None,actualQuality=None,productionPixels=False,historicalPreparationNotRewritten=True))
print(json.dumps(dict(planningCanvas=str(P),guides=len(guides),qa=len(qa),overlapsExact=True,AIInvoked=False)))

