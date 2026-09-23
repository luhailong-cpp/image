"""Fixed-existing-core boundary experiment; candidate only, no source edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, sys
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / 'tools'
PRODUCTION = HERE.parents[1]
OLD = PRODUCTION / 'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
V4 = HERE / 'repairs/versions/internal-v4'
RUN = HERE / 'external-v5'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p, box=None):
    with Image.open(p) as im: return np.array((im.crop(box) if box else im).convert('RGB'))
def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)
def main():
    assert not RUN.exists(), 'Preserve prior attempt'
    RUN.mkdir(); out = RUN/'output'; qa=RUN/'qa'; refs=RUN/'references'
    out.mkdir(); qa.mkdir(); refs.mkdir()
    left_core_path=TOOLS/'repairs/versions/r09_c09_repair_v6/r09_c09.png'
    left_ext_path=HERE/'references/latest-left-r09_c09-v6/extended-context.png'
    bottom_core_path=OLD/'r10_c10.png'; corner_core_path=OLD/'r10_c09.png'
    row_path=OLD/'row10-extended-context.png'
    sources=[V4/'r09_c10.png',V4/'repair.json',V4/'extended-context.png',left_core_path,left_ext_path,bottom_core_path,corner_core_path,row_path,OLD.parent/'assembly_v5.json']
    before={str(p):sha(p) for p in sources}
    assert sha(left_core_path)=='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
    original=load(V4/'extended-context.png'); v4=load(V4/'r09_c10.png')
    left_core=load(left_core_path); bottom_core=load(bottom_core_path); corner_core=load(corner_core_path)
    assert original.shape==(4326,4326,3) and np.array_equal(original[115:4211,115:4211],v4)
    left=load(left_ext_path,(4096,0,4326,4326)); bottom=load(row_path,(12288,0,16614,230))
    raw_left_corner=left[-230:].copy(); raw_bottom_corner=bottom[:,:230].copy()
    unified=np.empty((230,230,3),dtype=np.uint8)
    unified[:115,:115]=left_core[-115:,-115:]
    unified[115:,:115]=corner_core[:115,-115:]
    unified[115:,115:]=bottom_core[:115,:115]
    unified[:115,115:]=v4[-115:,:115]
    # Only reference halo ownership is corrected; all three existing tile cores stay unchanged.
    left[-230:]=unified; bottom[:,:230]=unified
    assert np.array_equal(left[-230:],bottom[:,:230])
    assert np.array_equal(left[115:4211,:115],left_core[:,-115:])
    assert np.array_equal(bottom[115:,115:4211],bottom_core[:115])
    assert np.array_equal(left[4211:,:115],corner_core[:115,-115:])
    diff={}
    for name,raw in [('left',raw_left_corner),('bottom',raw_bottom_corner)]:
        d=np.abs(raw.astype(np.int16)-unified.astype(np.int16))
        diff[name]={'changedPixels':int(np.any(d,axis=2).sum()),'meanAbsoluteDifference':float(d.mean()),'maxDifference':int(d.max())}
        Image.fromarray(raw).save(refs/f'{name}-corner-before.png')
        Image.fromarray(np.clip(d*4,0,255).astype(np.uint8)).save(refs/f'{name}-corner-difference-x4.png')
    Image.fromarray(unified).save(refs/'corner-after-owned-by-true-cores.png')
    Image.fromarray(left).save(refs/'left-context-owned.png');Image.fromarray(bottom).save(refs/'bottom-context-owned.png')
    context=original.copy(); context[:,:230]=left;context[4096:]=bottom
    x=np.arange(4326,dtype=np.float32)[None,:];y=np.arange(4326,dtype=np.float32)[:,None]
    mask=np.rint(255*smooth((x-115)/115)*smooth((4211-y)/115)).astype(np.uint8)
    sys.path.insert(0,str(TOOLS/'vendor'));sys.dont_write_bytecode=True
    hp=PRODUCTION/'tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('r09c10_fixed_join',hp)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    result,flow,correction,registration=helper.registered_join(context,original,mask,edges=('left','bottom'),max_shift=8.,flow_inner=300.,flow_full=120.,tone_inner=330.,tone_full=150.,match_tone=True)
    final=result[115:4211,115:4211].copy(); changed=np.any(final!=v4,axis=2)
    allowed=np.zeros((4096,4096),dtype=bool);allowed[:,:215]=True;allowed[3881:]=True
    assert not np.any(changed & ~allowed)
    assert np.array_equal(result[mask==0],context[mask==0])
    assert np.max(np.abs(flow))<=8.
    Image.fromarray(final).save(out/'r09_c10.png');Image.fromarray(result).save(out/'extended-context.png');Image.fromarray(mask).save(out/'mask.png')
    np.savez_compressed(out/'flow.npz',flow=flow);np.savez_compressed(out/'correction.npz',correction=correction)
    qa_files=[]
    def save(name,arr,role):
        p=qa/name;Image.fromarray(arr).save(p);qa_files.append({'file':str(p),'sha256':sha(p),'pixels':[arr.shape[1],arr.shape[0]],'role':role,'resized':False})
    def board(name,strip,role):
        assert strip.shape==(4096,320,3)
        save(name,np.concatenate([strip[i*1024:(i+1)*1024] for i in range(4)],axis=1),role)
    for version,candidate in [('before_internal_v4',v4),('after_external_v5',final)]:
        board(f'left-{version}-100pct.png',np.concatenate([left_core[:,-160:],candidate[:,:160]],axis=1),'Actual left-core boundary, four consecutive 1024px segments')
        strip=np.concatenate([candidate[-160:],bottom_core[:160]],axis=0)
        board(f'bottom-{version}-100pct.png',np.transpose(strip,(1,0,2)),'Actual bottom-core boundary; axes transposed; four consecutive source-x segments')
    board('left-treatment-return-x215-100pct.png',final[:,55:375],'Treatment return x=215')
    board('bottom-treatment-return-y3881-100pct.png',np.transpose(final[3721:4041],(1,0,2)),'Treatment return y=3881; axes transposed')
    four=np.concatenate([np.concatenate([left_core[-512:,-512:],final[-512:,:512]],axis=1),np.concatenate([corner_core[:512,-512:],bottom_core[:512,:512]],axis=1)],axis=0)
    save('four-tile-junction-100pct.png',four,'True existing three cores plus new candidate; 1024px native crop')
    save('southwest-treatment-return-100pct.png',final[3440:,:720],'New tile southwest transition return')
    preview=Image.fromarray(final);preview.thumbnail((1024,1024),Image.Resampling.LANCZOS);preview.save(qa/'overview-preview-only.png')
    assert all(sha(p)==h for p,h in before.items())
    report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'bounded_external_join_candidate_pending_visual_QA','candidate':{'file':str(out/'r09_c10.png'),'sha256':sha(out/'r09_c10.png'),'pixels':[4096,4096]},'sourceFiles':[{'file':p,'sha256':h} for p,h in before.items()],'script':{'file':str(Path(__file__).resolve()),'sha256':sha(__file__)},'helper':{'file':str(hp),'sha256':sha(hp)},'cornerOwnership':{'rawCornerExactEqual':bool(np.array_equal(raw_left_corner,raw_bottom_corner)),'rebuiltCornerExactEqual':True,'referenceOnlyReconstruction':True,'topLeft':'r09_c09 v6 bottom-right true core 115x115','bottomLeft':'r10_c09 old top-right true core 115x115','bottomRight':'r10_c10 old top-left true core 115x115','topRight':'r09_c10 internal-v4 bottom-left candidate 115x115; not established fixed neighbor','beforeAfterDifferences':diff,'allThreeExistingCoreConstraintsExact':True},'registration':registration,'changedCorePixels':int(changed.sum()),'allowedChangedCoreBands':{'leftX':[0,215],'bottomY':[3881,4096]},'outsideAllowedCoreBandsUnchanged':True,'sourceFilesUnchangedAfterVerified':True,'nativeArtEnlarged':False,'resampling':'Bounded max8px subpixel edge registration and local color matching; no enlargement','files':[{'file':str(p),'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()],'referenceFiles':[{'file':str(p),'sha256':sha(p)} for p in sorted(refs.iterdir()) if p.is_file()],'qa':qa_files,'actualModel':None,'actualQuality':None,'backendModelVerified':False,'visualAcceptancePassed':False,'productionAccepted':False,'runtimePublished':False}
    (RUN/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidate':report['candidate'],'corner':report['cornerOwnership'],'registration':registration,'qa':str(qa)},indent=2))
if __name__=='__main__': main()
