"""Combine disjoint local native edits over the pinned shared daytime geometry."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
from argparse import ArgumentParser
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):
    p=Path(p);im=Image.open(p)
    return {'file':str(p),'sha256':sha(p),'pixels':list(im.size)}
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ArgumentParser();p.add_argument('--west-core',required=True);p.add_argument('--west-mask',required=True);p.add_argument('--west-record',required=True);a=p.parse_args()
base=T/'shared-geometry/extended4326.png';original=np.array(Image.open(base).convert('RGB'))
ext=original.copy();core=ext[115:4211,115:4211];used=np.zeros((4326,4326),bool)
sw=T/'spring-edits/southwest';central=T/'spring-edits/central'
swimg=np.array(Image.open(sw/'candidate_with_halo.png').convert('RGB'));swmask=np.array(Image.open(sw/'mask-4326.png'))>0
assert swimg.shape==ext.shape and np.array_equal(swimg[~swmask],original[~swmask])
ext[swmask]=swimg[swmask];used|=swmask
inputs=[{'image':record(sw/'candidate_with_halo.png'),'mask':record(sw/'mask-4326.png'),'record':str(sw/'processing.json')}]
for name,ip,mp,rp in [('central',central/'edited-core4096.png',central/'alpha-mask-core4096.png',central/'composition-record.json'),('west_edge',Path(a.west_core),Path(a.west_mask),Path(a.west_record))]:
    img=np.array(Image.open(ip).convert('RGB'));m=np.array(Image.open(mp))>0
    assert img.shape==core.shape and m.shape==core.shape[:2]
    assert not np.any(m&used[115:4211,115:4211]),f'overlap with {name}'
    core[m]=img[m];used[115:4211,115:4211]|=m
    inputs.append({'name':name,'image':record(ip),'mask':record(mp),'record':str(rp),'recordSha256':sha(rp)})
assert np.array_equal(ext[~used],original[~used])
out=T/'selected';out.mkdir(exist_ok=True)
Image.fromarray(ext).save(out/'extended4326.png');Image.fromarray(core).save(out/'core4096.png')
Image.fromarray(used.astype('uint8')*255).save(out/'combined-mask-4326.png')
Image.fromarray(core).resize((1254,1254),Image.Resampling.LANCZOS).save(out/'preview1254.png')
re=np.array(Image.open(out/'extended4326.png'));rc=np.array(Image.open(out/'core4096.png'))
assert np.array_equal(re[115:4211,115:4211],rc)
assert np.array_equal(re[~used],original[~used])
outputs={n:record(out/n) for n in ['core4096.png','extended4326.png','preview1254.png','combined-mask-4326.png']}
wr(out/'delivery.manifest.json',{'schemaVersion':1,'appearance':'lanxian_spring','tile':'r08_c10','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'complete_native_candidate_pending_final_composite_review','base':record(base),'baseEvidence':str(T/'shared-geometry/source.json'),'inputs':inputs,'outputs':outputs,'assemblyResampling':None,'warp':None,'previewOnlyResampling':'LANCZOS downsample to1254; not final art','alreadyCompositedMaskPixelsCopiedWithoutSecondAlpha':True,'masksDisjoint':True,'outsideAllMasksByteEqual':True,'savedPngRereadExact':True,'coreMatchesExtended':True,'changedPixels':int(np.any(re!=original,axis=2).sum()),'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False})
print(json.dumps(outputs,ensure_ascii=False))
