from native_work import *
from PIL import ImageChops
p=ZONE/'qa/r03_c09-native-v1-20261016-local-seams16-verification.json';r=read(p);reused=[];new=[]
for e in r['inspectionEntries']:
    old=e.get('previousReview')
    if not old:continue
    previous=Image.open(old['evidence']).convert('RGB');current=Image.open(e['file']).convert('RGB');w,h=current.size;pw,ph=previous.size
    box=[(pw-w)//2,(ph-h)//2,(pw+w)//2,(ph+h)//2]
    same=bool(w<=pw and h<=ph and ImageChops.difference(previous.crop(box),current).getbbox() is None)
    old.update(previousEvidenceSize=[pw,ph],previousEvidenceCrop=box,exactCenteredCropPixelIdentical=same)
    if same and old['hashesMatch'] and old['status']=='passed_internal_only':e.update(status='passed_reused_source_hashes_and_exact_pixels',reviewMethod='prior100pctneighbor_review_reused_after_hash_and_center_crop_pixel_verification');reused.append(e['name'])
    else:new.append(e['name'])
write(p,r)
src=Path(current_references()[0]['file']);im=Image.open(src).convert('RGB');box=[v*1254/57344 for v in [32768,8192,36864,12288]];out=ZONE/'qa/r03_c09-native-v1-20261016-layout-authority-only.png';im.transform((768,768),Image.Transform.EXTENT,box,Image.Resampling.NEAREST).save(out)
write(out.with_suffix('.png.derivation.json'),{'source':src.as_posix(),'sourceSha256':sha(src),'sourceBox':box,'worldBox':[32768,8192,36864,12288],'outputSize':[768,768],'operation':'exact coordinate EXTENT nearest only for layout inspection','finalArt':False,'notNativeArt':True})
print(json.dumps({'reusedCount':len(reused),'reused':reused,'newSeams':new,'layoutReference':out.as_posix()}))
