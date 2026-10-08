from pathlib import Path
import datetime
import hashlib
import json
import numpy as np
from PIL import Image

P = Path(__file__).resolve().parent
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def norm(p): return str(p).replace('\\', '/')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data): Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def evidence(p): return {'file':norm(p),'sha256':sha(p)}

old = json.loads((P/'binding.json').read_text(encoding='utf-8-sig'))
history_path = P/'iteration-history.json'
history = json.loads(history_path.read_text(encoding='utf-8')) if history_path.exists() else {'iterations':[]}
if not any(x.get('createdAt') == old.get('createdAt') for x in history['iterations']):
    history['iterations'].append({'createdAt':old.get('createdAt'),'status':old.get('status'),'operation':old.get('operation'),'outputs':old.get('outputs'),'review':old.get('review'),'knownOutOfScope':old.get('knownOutOfScope'),'imageBackupsKept':False})
write(history_path, history)
ctx_record = json.loads((P/'context.png.generation.json').read_text(encoding='utf-8-sig'))
ctx = np.array(Image.open(P/'context.png').convert('RGB'))
native = np.array(Image.open(P/'native.png').convert('RGB'))
assert ctx.shape == native.shape == (1254,1254,3)
assert sha(P/'native.png') == old['nativeRepair']['sha256']
assert sha(P/'context.png') == old['sourceContext']['sha256']

regions = [
    {'id':'triangle','outerRectLTRB':[570,472,822,820],'fullAIWeightRectLTRB':[610,512,782,780]},
    {'id':'upper-gold-step','outerRectLTRB':[550,330,735,580],'fullAIWeightRectLTRB':[592,354,695,540]},
    {'id':'horizontal-gray-step','outerRectLTRB':[80,492,646,612],'fullAIWeightRectLTRB':[120,522,606,572]},
]
def axis_mask(n, outer0, core0, core1, outer1):
    x=np.arange(n,dtype=np.float32)
    a=np.clip((x-outer0)/(core0-outer0),0,1)
    b=np.clip((outer1-x)/(outer1-core1),0,1)
    t=np.minimum(a,b)
    return t*t*(3-2*t)
mask = np.zeros((1254,1254),dtype=np.float32)
for region in regions:
    l,t,r,b=region['outerRectLTRB']; il,it,ir,ib=region['fullAIWeightRectLTRB']
    local=np.outer(axis_mask(1254,t,it,ib,b),axis_mask(1254,l,il,ir,r))
    mask=np.maximum(mask,local)
alpha=np.rint(mask*255).astype(np.uint8)
mixed=np.rint(ctx.astype(np.float32)*(1-alpha[...,None]/255)+native.astype(np.float32)*(alpha[...,None]/255)).clip(0,255).astype(np.uint8)
assert np.array_equal(mixed[alpha==0],ctx[alpha==0])
Image.fromarray(alpha).save(P/'merge-mask.png')
Image.fromarray(mixed).save(P/'merged-context.png')
operation={'kind':'single_union_mask_native_coordinate_composite','sourcePixelScale':1,'sourceUpscaling':False,'sourceResampling':False,'geometricRegistration':None,'actualMechanicalDisplacementXY':[0,0],'colorCorrection':False,'imageBlur':False,'regions':regions,'union':'pixelwise maximum of smoothstep component masks; one composite against original context','mask':evidence(P/'merge-mask.png'),'maskZeroPixelsUnchanged':True}
base={'createdAt':now(),'iteration':'union-v2','formalAccepted':False,'clientVerified':False,'productionSelectionChanged':False,'operation':operation}
write(P/'merge-mask.png.generation.json',{**base,**evidence(P/'merge-mask.png'),'operationPurpose':'mechanical alpha mask only; no generated art'})
write(P/'merged-context.png.generation.json',{**base,**evidence(P/'merged-context.png'),'width':1254,'height':1254,'derivedFrom':[evidence(P/'context.png'),evidence(P/'native.png')]})
outputs=[]; unchanged=[]; exported={}
for part in ctx_record['parts']:
    source=Path(part['source']['path']); assert sha(source)==part['source']['sha256']
    original=np.array(Image.open(source).convert('RGB')); result=original.copy()
    l,t,r,b=part['cropLTRB']; px,py=part['pasteXY']; patch=mixed[py:py+b-t,px:px+r-l]
    result[t:b,l:r]=patch
    out=P/'coupled'/f'{part["tile"]}.png'; Image.fromarray(result).save(out)
    changed=np.any(result!=original,axis=2); ys,xs=np.where(changed)
    box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
    row={'tileId':part['tile'],'path':norm(out),'sha256':sha(out),'sourcePath':norm(source),'sourceSha256':sha(source),'changedPixelCount':int(changed.sum()),'changedBoundingBoxLTRB':box,'generationRecord':norm(Path(str(out)+'.generation.json'))}
    outputs.append(row); exported[part['tile']]=Image.fromarray(result)
    write(str(out)+'.generation.json',{**base,**evidence(out),'width':4096,'height':4096,'derivedFrom':[evidence(source),evidence(P/'merged-context.png')],'changedPixelCount':row['changedPixelCount'],'changedBoundingBoxLTRB':box,'status':'pending_actual_native_review'})
    unchanged.append({'file':norm(source),'expectedSha256':part['source']['sha256'],'observedSha256':sha(source),'matches':sha(source)==part['source']['sha256']})
# Reconstruct all QA from the actual saved outputs, never from the in-memory draft.
current=Image.new('RGB',(1254,1254))
for part in ctx_record['parts']: current.paste(exported[part['tile']].crop(part['cropLTRB']),tuple(part['pasteXY']))
assert np.array_equal(np.array(current),mixed)
qa=[]
def save_qa(name,rects,before_after=False):
    crops=[current.crop(tuple(r)) for r in rects]
    if before_after:
        assert len(rects)==1
        crops=[Image.fromarray(ctx).crop(tuple(rects[0])),crops[0]]
    width=sum(i.width for i in crops)+12*(len(crops)-1); height=max(i.height for i in crops)
    board=Image.new('RGB',(width,height),(30,35,45)); x=0; mappings=[]
    for idx,crop in enumerate(crops):
        board.paste(crop,(x,0)); mappings.append({'boardRectLTRB':[x,0,x+crop.width,crop.height],'contextRectLTRB':rects[0] if before_after else rects[idx],'source':'original' if before_after and idx==0 else 'actual_exported_coupled_tiles'}); x+=crop.width+12
    out=P/'qa'/('union-v2-'+name+'.png'); board.save(out)
    row={**evidence(out),'scope':name,'width':width,'height':height,'nativeScale':1,'resized':False,'mappings':mappings,'actuallyViewed':False,'derivedFromOutputs':outputs}
    qa.append(row); write(str(out)+'.generation.json',{**base,**row})
save_qa('whole-local',[[40,280,922,920]])
save_qa('triangle-before-after',[[530,432,862,860]],True)
save_qa('gold-before-after',[[510,290,775,620]],True)
save_qa('gray-before-after',[[40,452,686,652]],True)
for rg in regions:
    l,t,r,b=rg['outerRectLTRB']
    save_qa(rg['id']+'-side-returns',[[max(0,l-40),max(0,t-30),l+60,min(1254,b+30)],[r-60,max(0,t-30),min(1254,r+40),min(1254,b+30)]])
    save_qa(rg['id']+'-top-bottom-returns',[[max(0,l-30),max(0,t-40),min(1254,r+30),t+60],[max(0,l-30),b-60,min(1254,r+30),min(1254,b+40)]])
binding={**base,'status':'union_v2_three_target_improvements_pending_native_review','sourceContext':evidence(P/'context.png'),'nativeRepair':{**evidence(P/'native.png'),'generationRecord':norm(P/'native.png.generation.json')},'outputs':outputs,'qa':qa,'sourceUnchanged':unchanged,'allOtherPixelsUnchanged':True,'fullCityOrTileAcceptance':False,'doNotAutoPromote':True,'knownOutOfScope':['Upper x627 gray-slab boundary outside these ROIs','Rest of c07/c08 common edge and all other old defects','Missing neighbors, whole-city and client/runtime acceptance'],'iterationHistory':evidence(history_path)}
write(P/'binding.json',binding)
write(P/'review.json',{'reviewedAt':None,'status':'pending_actual_native_review','outputs':outputs,'qa':qa,'formalAccepted':False,'entireSharedEdgePassed':False})
print(json.dumps({'binding':norm(P/'binding.json'),'outputs':outputs,'qaCount':len(qa)},ensure_ascii=True))
