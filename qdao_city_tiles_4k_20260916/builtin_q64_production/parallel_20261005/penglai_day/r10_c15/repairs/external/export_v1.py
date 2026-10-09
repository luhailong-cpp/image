from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h;import quilt as q
state=json.loads((O/'state-v1.json').read_text(encoding='utf8'));P=O/'proposals';P.mkdir(exist_ok=True)
base=Path(state['base']['file']);own=Image.open(base).convert('RGB');own0=np.asarray(own).copy()
manifest={'selfBase':state['base'],'neighborProposals':{},'sharedJointSources':{},'cornerProtectionException':json.loads((O/'corner-protection-exception.json').read_text(encoding='utf8')),'formalAccepted':False}
for axis,ver in [('north','v4'),('west','v2')]:
 jp=O/(axis+'-joint-candidate-'+ver+'.png');mp=O/(axis+'-'+ver+'-mask.png');j=Image.open(jp).convert('RGB');m=Image.open(mp).convert('L');src=Path(state['neighbors'][axis]['file']);other=Image.open(src).convert('RGB');orig=np.asarray(other).copy()
 if axis=='north':
  other.paste(j.crop((0,0,4096,627)),(0,3469));own.paste(j.crop((0,627,4096,1254)),(0,0),m.crop((0,627,4096,1254)))
 else:
  other.paste(j.crop((0,0,627,4096)),(3469,0));own.paste(j.crop((627,0,1254,4096)),(0,0),m.crop((627,0,1254,4096)))
 tile='r09_c15' if axis=='north' else 'r10_c14';dest=P/(tile+'-'+axis+'-proposal-v1.png');other.save(dest);h.derived(dest,[src,jp,mp],{'method':'exactnative shared627 edge replacement; neighbor unchanged outside actual diffmask','sourceBaseSha256':h.sha(src)})
 diff=np.any(np.asarray(other)!=orig,axis=2);mask=Image.fromarray(diff.astype('uint8')*255);dm=P/(tile+'-'+axis+'-actual-diff-mask-v1.png');mask.save(dm);h.derived(dm,[src,dest],{'method':'exact per-pixel RGB difference binary mask','outsideChanges':0})
 assert np.array_equal(np.asarray(other)[~diff],orig[~diff])
 manifest['neighborProposals'][axis]={'tile':tile,'base':str(src),'baseSha256':h.sha(src),'candidate':str(dest),'sha256':h.sha(dest),'mask':str(dm),'maskSha256':h.sha(dm),'bbox':mask.getbbox(),'changedPixels':int(diff.sum()),'outsideMaskChanges':0,'bottom115ChangedPixels':int(diff[3981:].sum()),'bottom115ChangedBBox':Image.fromarray(diff[3981:].astype('uint8')*255).getbbox()}
 manifest['sharedJointSources'][axis]={'file':str(jp),'sha256':h.sha(jp),'mask':str(mp),'maskSha256':h.sha(mp),'globalOrigin':state['jointOrigins'][axis]}
dest=R/'tiles/r10_c15-candidate-review-v1.png';own.save(dest);h.derived(dest,[base]+[Path(v['file']) for v in manifest['sharedJointSources'].values()]+[Path(v['mask']) for v in manifest['sharedJointSources'].values()],{'method':'north/west exact masks on internally repaired native4096 with rootcorner; no resampling','globalRectXYWH':[57344,36864,4096,4096]})
diff=np.any(np.asarray(own)!=own0,axis=2);mp=P/'r10_c15-external-actual-diff-mask-v1.png';im=Image.fromarray(diff.astype('uint8')*255);im.save(mp);h.derived(mp,[base,dest],{'method':'exact actual difference'})
manifest['selfCandidate']={'file':str(dest),'sha256':h.sha(dest),'maskFromCornerBase':str(mp),'maskSha256':h.sha(mp),'bbox':im.getbbox(),'changedPixels':int(diff.sum())}
raw=R/'tiles/r10_c15-candidate.png';di=np.any(np.asarray(own)!=np.asarray(Image.open(raw)),axis=2);fp=P/'r10_c15-all-changes-from-raw-mask-v1.png';im=Image.fromarray(di.astype('uint8')*255);im.save(fp);h.derived(fp,[raw,dest],{'method':'exact per-pixel diff from original16native core assembly'});manifest['allChangesFromRaw']={'file':str(fp),'sha256':h.sha(fp),'bbox':im.getbbox(),'changedPixels':int(di.sum())}
p=R/'preview-review-v1.png';own.resize((1254,1254),Image.Resampling.LANCZOS).save(p);h.derived(p,[dest],{'method':'review-only preview downscale'})
q.O=R/'qa';q.qa(np.asarray(own),'review-v1',dest)
for axis,v in manifest['sharedJointSources'].items():
 img=Image.open(v['file']);src=Path(v['file'])
 for k,pos in enumerate([557,1139,2163,3072]):
  box=(max(0,pos-160),280,min(4096,pos+160),1160) if axis=='north' else (150,max(0,pos-160),1110,min(4096,pos+160))
  p=R/'qa'/f'{axis}-return-{pos}-v1.png';img.crop(box).save(p);h.derived(p,[src],{'method':'native joint return crop','boxLTRB':box})
(O/'handoff-review-v1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(manifest['neighborProposals'],indent=2))
print('SELF',str(dest),h.sha(dest))
