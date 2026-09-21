import hashlib,json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path('E:/work/image/qdao_city_tiles_4k_20260916');B=R/'builtin_q64_production';A=B/'penglai_joint_c12_batch_20260917';J=B/'penglai_mid_autumn/r09_c10_c11_c12_joint';O=J/'output_v2_20260920';Q=J/'qa_v2_20260920'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).relative_to(R).as_posix()
outqa=J/'visual-review-v2-20260920.json';ledger=A/'mid-v2-ledger-update-20260920.json';assert not outqa.exists() and not ledger.exists()
asm=read(O/'assembly.json');assert sha(asm['parentAssembly'])==asm['parentAssemblySha256'];assert sha(asm['parentExtendedContext'])==asm['parentExtendedContextSha256']
script=B/'penglai_mid_autumn/r09_c12/assemble_builtin_v2_20260920.py';sp=importlib.util.spec_from_file_location('a',script);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
_,entries=mod.load_sources();basevalidation=mod.validate_saved(read(script.parent/'output_v2_20260920/assembly.json'),entries)
old=np.array(Image.open(asm['parentExtendedContext']));new=np.array(Image.open(O/'extended-context.png'));changed=np.zeros(old.shape[:2],bool)
for repair in asm['repairs']:
    for key in ('mask','flow','colorCorrection'):assert sha(repair[key]['path'])==repair[key]['sha256']
    assert sha(repair['nativeSource'])==repair['nativeSha256'];assert sha(repair['record'])==repair['recordSha256']
    rec=read(repair['record']);assert sha(rec['sourceOutputPath'])==rec['outputSha256'];assert sha(rec['promptFile'])==rec['promptSha256']
    for ref in rec['submittedImages']:assert sha(ref['path'])==ref['sha256']
    x,y,r,b=repair['sourceCropLTRB'];changed[y+115:b+115,x+115:r+115]|=np.array(Image.open(repair['mask']['path']))>0
assert np.array_equal(old[~changed],new[~changed]) and np.array_equal(old[:,:4211],new[:,:4211])
triple=np.array(Image.open(O/'triple-12288x4096.png'));assert np.array_equal(new[115:4211,115:12403],triple)
tiles=[e for e in asm['outputs'] if e['kind']=='tile'];assert len(tiles)==3
for e in asm['outputs']:assert sha(e['file'])==e['sha256']
assert np.array_equal(np.concatenate([np.array(Image.open(e['file'])) for e in tiles],axis=1),triple)
fresh={'overview.png','boundary_x8192_y2048.png','boundary_x8192_y2842.png','internal_y3072.png','junction_x8192_y1024.png','junction_x8192_y2048.png','junction_x8192_y3072.png','repair-overlap.png'}
evidence=[]
for e in asm['qa']:
    p=Path(e['file']);assert sha(p)==e['sha256'];item=dict(e)
    if p.name in fresh or p.name.startswith('water-'):item['reviewMethod']='view_image original of final v2 in current session; overview downsampled preview only'
    else:
        parent=J/'qa_v1_20260920'/p.name;assert sha(parent)==sha(p)
        item['reviewMethod']='view_image original of v1 in current session; exact PNG hash equals final v2';item['viewedPath']=str(parent)
    evidence.append(item)
oldqa=B/'penglai_mid_autumn/r09_c10_c11_joint/qa/v3/visual-review.json'
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'penglai_mid_autumn','version':'output_v2_20260920','status':'local_continuity_review_passed_candidate_only','approvedForRootMerge':True,'assembly':str(O/'assembly.json'),'assemblySha256':sha(O/'assembly.json'),'sourceTriple':str(O/'triple-12288x4096.png'),'sourceTripleSha256':sha(O/'triple-12288x4096.png'),'visualEvidence':evidence,'visualFindings':['Six full c12 internal lines and all nine internal junctions are continuous in paving, lantern, bridge and rail.','Both four-slice shared boundaries were reviewed at native scale. Historical c10/c11 paving remains softer as previously recorded, but no new structural break; c10 untouched.','The definitive c11/c12 water brightness/reflection-density splice was corrected using two native redraws. Both support crops, all eight actual ROI return edges, their overlap, the full updated lower boundary and its y3072 intersection pass local continuity review. Cyan reflection paths remain connected without a narrow vertical stripe or duplicate outline.','Lower repair uses existing bottom halo and returns at triple y4140, outside the effective tile y4096; this inspected local context does not accept a future neighbor.'],'previousPairReview':{'path':str(oldqa),'sha256':sha(oldqa)},'mechanical':{'baseNativeSourceCount':16,'baseSourceAndGuideValidation':basevalidation,'repairNativeCount':2,'sourceBytesPreserved':True,'threeTiles4096Square':True,'splitIdentity':True,'outerCropIdentity':True,'zeroMaskPixelsUnchanged':True,'c10Unchanged':True,'repairSourceAndFieldHashesVerified':True},'processingDisclosure':asm['sourceResampling'],'newNativeImagesGenerated':2,'formallyAccepted':False,'wholeCityAccepted':False,'runtimePublished':False,'remainingAcceptance':['other external neighbors','cross-appearance microgeometry including historical ornaments','full 256-tile city','foreground and navigation','Unity nearest camera movement seasonal switch device performance']}
outqa.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
candidates=[]
for k,e in enumerate(tiles):
    col=k+10;p=Path(e['file']);assert Image.open(p).size==(4096,4096)
    candidates.append({'appearance':'penglai_mid_autumn','displayName':'蓬莱仙岛中秋','tile':f'r09_c{col}','file':rel(p),'sha256':sha(p),'assembly':rel(O/'assembly.json'),'qa':rel(outqa),'pixels':[4096,4096],'finalPixelRectXYWH':[(col-1)*4096,32768,4096,4096],'worldRect':{'x':50+(col-1)*18.75,'z':131.25,'width':18.75,'height':18.75},'status':'candidate_local_continuity_reviewed_not_runtime_accepted','accepted':False,'runtimePublished':False})
data={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'batch':'penglai_mid_autumn_c12_local_qa_20260920','status':'ready_for_root_merge','candidates':candidates,'repairRecords':[rel(x['record']) for x in asm['repairs']],'newUniqueCandidates':1,'replacementCandidates':2,'newNativeSources':2,'sourceAccountingNote':'All 16 existing c12 base native sources were already counted in 20260919 source-only merge; only these two water repairs are new.','qa':str(outqa),'runtimePublished':False,'formalAcceptance':False}
ledger.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(str(ledger))
