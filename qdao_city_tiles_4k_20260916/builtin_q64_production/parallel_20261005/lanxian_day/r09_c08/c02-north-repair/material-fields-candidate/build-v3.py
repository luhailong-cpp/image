from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08/c02-north-repair/material-fields-candidate');V=D/'v3';V.mkdir(exist_ok=True);src=D/'v2/candidate1254.png';a=np.array(Image.open(src).convert('RGB'));z=a.astype(np.float32);Y,X=np.mgrid[:1254,:1254]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p,role):return {'file':str(p),'sha256':sha(p),'role':role}
def smooth(z):
 z=np.clip(z,0,1);return z*z*(3-2*z)
up=np.median(z[113:115],axis=0);lo=np.median(z[115:117],axis=0)
coef=np.array([np.polyfit(lo[:145,c],up[:145,c],1) for c in range(3)],np.float32)
rr,gg,bb=z[...,0],z[...,1],z[...,2]
alpha=smooth((155-rr)/25)*smooth((rr-gg-10)/18)*smooth((gg-bb-5)/12)
alpha*=1-smooth((X-120)/25);alpha*=1-smooth((Y-125)/60);alpha*=((X<145)&(Y>=115)&(Y<185))
mapped=z*coef[:,0]+coef[:,1];bounded=np.clip(mapped-z,-np.array([24,16,10]),np.array([24,16,10]));bf=(bounded*alpha[...,None]).astype(np.float32)
out=np.rint(np.clip(z+bf,0,255)).astype(np.uint8);assert np.array_equal(out[:115],a[:115]);assert np.array_equal(out[400:],a[400:]);assert np.array_equal(out[:,430:],a[:,430:])
Image.fromarray(out).save(V/'candidate1254.png');Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(V/'brown-alpha.png')
changed=np.any(out!=a,axis=-1);Image.fromarray(np.uint8(changed)*255).save(V/'brown-changed-mask.png')
fields=np.load(D/'v2/fields.npz')
np.savez_compressed(V/'brown-fields.npz',brown_rgb_field=bf,brown_alpha=alpha,channel_affine_scale_bias=coef,source_v2_pixels=a,reference_north_last2=a[113:115],reference_south_first2=a[115:117],limits=np.array([24,16,10]))
joined=np.array(Image.open(D/'v2/north1254x512.png').convert('RGB'));joined[256:]=out[115:371];Image.fromarray(joined).save(V/'north1254x512.png')
for name,box in [('orange-plus-brown',[0,216,430,356]),('brown',[0,216,180,326]),('leaves-unchanged',[990,206,1254,346])]:Image.fromarray(joined).crop(box).save(V/(name+'.png'))
ys,xs=np.where(alpha>0)
meta={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'operation':'Single per-channel affine color mapping inside deep brown inner-tree/soil material; no geometry/no AI/no image blur','status':'candidate_pending_actual_review_not_adopted','source':ref(src,'Exact v2 orange/leaf candidate baseline'), 'inheritV2':ref(D/'v2/manifest.json','Unchanged v2 processing and selected fields'),'sourceV4':ref(D.parent/'candidate-v4/candidate1254.png','Original baseline for any future merged operation'),'fit':'Per-channel least-squares affine from actual south first2 column medians to true north last2 column medians, columns0..144; no per-column correction values; fixed3scale+bias coefficients apply only through material alpha','channelScaleBias':coef.tolist(),'limit':[24,16,10],'actualFloatMin':bf.min(axis=(0,1)).tolist(),'actualFloatMax':bf.max(axis=(0,1)).tolist(),'alphaBoxXYXY':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'alphaFormula':'Smooth confidence R<155 and R-G>10 and G-B>5; x120..145 smooth fade, y125..185 smooth fade; trueNorth y<115 and x>=145 unchanged. Orange/highlight pixels excluded by high R.','unchangedTrueNorth115':True,'unchangedRows400To1253':True,'unchangedWoodSeatX430Plus':True,'unchangedV2OrangeAndLeafOutsideBrownSupport':True,'mergeRule':'Inherit v2 collision checks against original v4. For brown delta require future source pixel equals saved source_v2_pixels at every affected pixel; apply no geometry and reject conflicts. Brown field bounded separately and cannot touch wood seat.','technicalArtifacts':[ref(V/'brown-alpha.png','Brown material continuous alpha'),ref(V/'brown-changed-mask.png','Exact brown changed support'),ref(V/'brown-fields.npz','Brown RGB field and affine coefficients with source guard pixels')],'outputs':[ref(V/f,'Candidate or exact original-pixel QA') for f in ['candidate1254.png','north1254x512.png','orange-plus-brown.png','brown.png','leaves-unchanged.png']],'formalAccepted':False}
(V/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'coef':coef.tolist(),'actualMin':meta['actualFloatMin'],'actualMax':meta['actualFloatMax'],'support':meta['alphaBoxXYXY']}))

