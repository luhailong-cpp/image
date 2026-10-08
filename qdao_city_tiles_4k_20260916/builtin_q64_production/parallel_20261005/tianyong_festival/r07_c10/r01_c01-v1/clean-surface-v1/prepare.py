from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent;P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
source=P/'final-v1/joined.png'
assert sha(source)=='1591d87168428c2f075b9728d41e2fdf650b830fa8f2029e11b54156adb2e7a8'
im=Image.open(source).convert('RGBA');a=np.array(im);a[350:680,510:865]=0
Image.fromarray(a).save(D/'context.png')
im.crop((480,320,900,710)).save(D/'defect-before.png')
im.crop((270,0,430,140)).save(D/'halo-chip-excluded.png')
prompt="""Use case: precise-object-edit. Restore only the single transparent rectangle x510..864,y350..679 in this1254x1254 exact source picture. It is a small surface repair to ONE existing ivory floor slab in a bright clean rounded DaoistQ game plaza. Fill the missing surface with the same soft painted warm ivory stone, gently mottled at the same scale. Remove the thin long diagonal crack/creased triangular depression previously crossing this rectangle. The slab must be flat and intact: NO fissure, crack, crease, angular scratch, missing chip, seam, diagonal groove, fold or gash within its flat face. Keep the existing slate/ivory palette and subtly varied hand-painted finish. No blur or smearing. Reconstruct the short portion of the existing LOWER WHITE BEVEL AND BROWN SEPARATING JOINT that passes through the bottom of the rectangle in exactly the same straight diagonal path, width, elevation, and endpoints from both visible sides. That genuine slab border must remain sharp and unchanged. Keep every other visible pixel, all slab boundaries, broad ring courses, framing, camera and lighting fixed. Do not add objects, decoration, text, UI, paving joints or detail. Image2 is approved paint style reference only; do not copy its UI."""
refs=[D/'context.png',Path(r'D:/work/image/designs/gameplay-ui/04-guild.png')]
request={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'source':info(source),'configSnapshot':json.loads(Path(r'D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),'sameBatchCapabilityEvidence':info(T/'r08_c10/r01_c01-v1/model-capability.json'),'references':[dict(info(refs[0]),role='native edit context'),dict(info(refs[1]),role='approved style only')],'maskNativeLTRB':[510,350,865,680],'windowTileLocalLTRB':[-115,-115,1139,1139],'intendedRepairTileLocalLTRB':[395,235,750,565],'excludedFinding':{'nativeLTRB':[300,20,390,100],'tileLocalLTRB':[185,-95,275,-15],'reason':'Entire sharp triangular chip lies within top115halo outside current r07_c10 tile; no current-tile ROI exists, excluded from this delivery.'}}
(D/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8');(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps(request))
