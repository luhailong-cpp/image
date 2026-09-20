"""Mechanical join of selected historical pair v3 and new c12. No source resize."""
import hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
B=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
C=B/'penglai_mid_autumn'; J=C/'r09_c10_c11_c12_joint'; O=J/'output_v1_20260920'; Q=J/'qa_v1_20260920'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not O.exists() and not Q.exists()
    left=C/'r09_c10_c11_joint/output/v3/extended-context.png'
    right=C/'r09_c12/output_v2_20260920/extended-context.png'
    script=C/'r09_c12/assemble_builtin_v2_20260920.py'
    spec=importlib.util.spec_from_file_location('assembler',script); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    _,entries=m.load_sources(); validated=m.validate_saved(m.read_json(right.parent/'assembly.json'),entries)
    l=np.array(Image.open(left).convert('RGB'));r=np.array(Image.open(right).convert('RGB'))
    assert l.shape==(4326,8422,3) and r.shape==(4326,4326,3)
    ext,metric=m.append_patch(l,r,m.load_seam_helper(),'r09_c11_c12')
    assert ext.shape==(4326,12518,3) and np.array_equal(ext[:,:8192],l[:,:8192]) and np.array_equal(ext[:,8422:],r[:,230:])
    O.mkdir(parents=True);Q.mkdir()
    full=Image.fromarray(ext);triple=full.crop((115,115,12403,4211)); files=[]; qa=[]
    def save(im,p,kind='candidate',crop=None):
        im.save(p);item={'file':str(p),'pixels':list(im.size),'sha256':sha(p),'kind':kind}
        if crop: item['cropLTRB']=crop
        (qa if p.parent==Q else files).append(item)
    save(full,O/'extended-context.png');save(triple,O/'triple-12288x4096.png')
    for col in range(3):
        p=O/f'penglai_mid_autumn_r09_c{10+col:02d}_4k_joint_candidate_v1.png'
        save(triple.crop((4096*col,0,4096*(col+1),4096)),p)
        assert np.array_equal(np.array(Image.open(p)),np.array(triple)[:,4096*col:4096*(col+1)])
    save(triple.resize((2048,683),Image.Resampling.LANCZOS),Q/'overview.png','preview_only')
    for x in (4096,8192):
        for y in (0,1024,2048,2842):
            box=[x-627,y,x+627,y+1254];save(triple.crop(box),Q/f'boundary_x{x}_y{y:04d}.png','native_crop',box)
    rt=triple.crop((8192,0,12288,4096))
    for axis in ('x','y'):
        for pos in (1024,2048,3072):
            strip=rt.crop((pos-150,0,pos+150,4096)) if axis=='x' else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
            sheet=Image.new('RGB',(1200,1024))
            for k in range(4): sheet.paste(strip.crop((0,1024*k,300,1024*(k+1))),(k*300,0))
            save(sheet,Q/f'internal_{axis}{pos}.png','native_fullseam_panels')
    for y in (1024,2048,3072):
        for x in (8192,9216,10240,11264):
            box=[x-450,y-450,x+450,y+450];save(triple.crop(box),Q/f'junction_x{x}_y{y}.png','native_crop',box)
    records=[]
    for p in (left,right):
        a=p.parent/'assembly.json';records.append({'contextPath':str(p),'contextSha256':sha(p),'assemblyPath':str(a),'assemblySha256':sha(a)})
    report={'schemaVersion':1,'appearance':'penglai_mid_autumn','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA_not_published','runtimePublished':False,'formallyAccepted':False,'sources':records,'scriptPath':str(Path(__file__)),'scriptSha256':sha(__file__),'geometry':{'joinedPixels':[12518,4326],'cropLTRB':[115,115,12403,4211],'triplePixels':[12288,4096],'tilePixels':[4096,4096],'overlap':230,'globalPixelRectXYWH':[36864,32768,12288,4096]},'method':'minimum-error native overlap seam; 2px feather; exact split','jointStageResampling':False,'sourceArtUpscaled':False,'upstreamProcessing':'Historical pair v3 includes limited native repair registration; see source manifests.','unchangedOutsideOverlap':True,'splitPixelIdentity':True,'singleTileMechanicalValidation':validated,'seamMetric':metric,'outputs':files,'qa':qa,'visualStatus':'pending','externalNeighbors':'unverified','runtimeAccepted':False}
    (O/'assembly.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(O),'qa':str(Q),'passedMechanical':True}))
if __name__=='__main__':main()
