from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;ROOT=next(p for p in N.parents if (p/'config/image-generation.json').exists());D=T/'r07_c08/preparation-v1';D.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'file':str(p),'sha256':sha(p)};save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
root=read(T/'source-checkpoint.json');s={k:next(v for v in root['candidateSet'] if v['tile']==k) for k in ['r07_c09','r08_c08','r08_c09']}
for v in s.values():assert sha(v['file'])==v['sha256']
regions=[('r07_c09',[0,2957,115,4096],[1139,0]),('r08_c08',[2957,0,4096,115],[0,1139]),('r08_c09',[0,0,115,115],[1139,1139])]
C=Image.new('RGBA',(1254,1254));known=[]
for k,b,xy in regions:
 a=Image.open(s[k]['file']).convert('RGBA').crop(b);assert np.all(np.array(a)[:,:,3]==255);C.paste(a,xy);known.append({'source':s[k],'sourceLTRB':b,'contextXY':xy})
C.save(D/'context.png');origin=[28672,24576];local=[2957,2957,4211,4211];world=[origin[i%2]+local[i] for i in range(4)];M=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(M)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
G=Image.open(M).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world));G.save(D/'layout-reference-only.png');G=G.convert('RGBA');G.alpha_composite(C);G.convert('RGB').save(D/'coarse-layout-with-native-anchors-reference-only.png')
save(D/'root-checkpoint-frozen.json',root)
plan={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c08','tileGlobalOrigin':origin,'firstPatch':{'name':'r04_c04','nativeCanvas':[1254,1254],'tileLocalLTRB':local,'globalLTRB':world,'newCoreTileLocalLTRB':[2957,2957,4096,4096],'knownRegions':known,'context':ref(D/'context.png')},'sources':s,'sourceCheckpoint':ref(D/'root-checkpoint-frozen.json'),'canonicalMaster':ref(M),'guide':ref(D/'layout-reference-only.png'),'compositeInputOnly':ref(D/'coarse-layout-with-native-anchors-reference-only.png'),'styleReference':ref(ROOT/'designs/gameplay-ui/04-guild.png'),'progression':'Bottom row right to left, then successive rows upward; adapt window offsets only when actual native geometry needs it. Never fill beyond unknown own ROI except explicit finite coupled returns.','plannedCoupledReturnsFirstPatch':[{'tile':'r07_c09','roi':[0,2957,61,4096]},{'tile':'r08_c08','roi':[2957,0,4096,61]},{'tile':'r08_c09','roi':[0,0,61,61]}],'generationStarted':False,'formalAccepted':False,'nativeScale':1,'guidePixelsAllowedInFinal':False,'route':'builtin image_gen','actualModel':None,'actualQuality':None,'checksBeforeGeneration':['Re-freeze latest root source and verify exact known ROI; preserve any new northern/eastern updates outside finite return ROI.','Inspect first-patch guide/native endpoints in same world coords; use genuine native contours if guide differs.','Inspect known existing r08c08/r08c09 vertical corner seam before classifying a new r07c08 failure.'],'northAndWestActualNeighbors':'pending unknown','rootStateModified':False}
save(D/'context-plan.json',plan)
print(json.dumps({'directory':str(D),'world':world,'plan':ref(D/'context-plan.json')}))
