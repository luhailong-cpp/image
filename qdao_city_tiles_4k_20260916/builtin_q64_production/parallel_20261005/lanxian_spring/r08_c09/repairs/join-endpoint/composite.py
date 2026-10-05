from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savej(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def imginfo(p,role):
    with Image.open(p) as im:size=list(im.size);mode=im.mode
    return {'file':str(p),'sha256':sha(p),'pixels':size,'mode':mode,'role':role}
target=read(OUT/'edit-target-1254.derived.json');tool=read(OUT/'tool-result.json')
src=Path(target['coreSource']);src_halo=Path(target['haloSource'])
assert sha(src)==target['coreSourceSha256'];assert sha(src_halo)==target['haloSourceSha256']
gen=Path(tool['originalToolFile']); raw=OUT/'generated-original-1254.png'
shutil.copyfile(gen,raw)
with Image.open(src) as im:a=np.asarray(im.convert('RGB')).copy()
with Image.open(src_halo) as im:h=np.asarray(im.convert('RGB')).copy()
with Image.open(raw) as im:g=np.asarray(im.convert('RGB')).copy();assert im.size==(1254,1254)
assert np.array_equal(h[115:4211,115:4211],a)
box=(1000,930,1300,1160); crop=(509,413,1763,1667)
x1,y1,x2,y2=box;w=x2-x1;hh=y2-y1;feather=36
yy,xx=np.mgrid[0:hh,0:w]
dist=np.minimum(np.minimum(xx,w-1-xx),np.minimum(yy,hh-1-yy))
alpha=np.rint(255*(0.5-0.5*np.cos(np.pi*np.clip(dist/feather,0,1)))).astype(np.uint8)
mask=np.zeros((4096,4096),np.uint8);mask[y1:y2,x1:x2]=alpha
maskcrop=mask[crop[1]:crop[3],crop[0]:crop[2]]
Image.fromarray(mask).save(OUT/'repair-mask-core4096.png')
Image.fromarray(maskcrop).save(OUT/'repair-mask-crop1254.png')
rawroi=g[y1-crop[1]:y2-crop[1],x1-crop[0]:x2-crop[0]]
oldroi=a[y1:y2,x1:x2]
blend=((rawroi.astype(np.uint32)*alpha[:,:,None]+oldroi.astype(np.uint32)*(255-alpha[:,:,None])+127)//255).astype(np.uint8)
candidate=a.copy();candidate[y1:y2,x1:x2]=blend
candidate_halo=h.copy();candidate_halo[115:4211,115:4211]=candidate
core_out=OUT/'candidate_4096.png';halo_out=OUT/'candidate_with_halo.png'
Image.fromarray(candidate).save(core_out);Image.fromarray(candidate_halo).save(halo_out)
changed=np.any(candidate!=a,axis=2);sy,sx=np.where(changed)
outerequal=bool(np.array_equal(candidate[mask==0],a[mask==0]));assert outerequal
assert np.array_equal(candidate_halo[115:4211,115:4211],candidate)
hm=np.zeros((4326,4326),bool);hm[115:4211,115:4211]=mask!=0
assert np.array_equal(candidate_halo[~hm],h[~hm])
assert np.array_equal(candidate[:,:230],a[:,:230])
assert np.array_equal(candidate[:,-230:],a[:,-230:])
assert np.array_equal(candidate_halo[:,:230],h[:,:230])
assert np.array_equal(candidate_halo[:,4096:],h[:,4096:])
assert sha(src)==target['coreSourceSha256'];assert sha(src_halo)==target['haloSourceSha256']
qa=(996,916,1316,1176)
def cut(arr,b):return Image.fromarray(arr[b[1]:b[3],b[0]:b[2]])
cut(candidate,qa).save(OUT/'after-local-320x260.png')
cut(candidate,crop).save(OUT/'after-context-1254.png')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
panel=Image.new('RGB',(640,296),'#eee9dc');d=ImageDraw.Draw(panel)
d.text((10,10),'Before - actual pixels',fill='black',font=font);d.text((330,10),'After - actual pixels',fill='black',font=font)
panel.paste(cut(a,qa),(0,36));panel.paste(cut(candidate,qa),(320,36));panel.save(OUT/'qa-before-after.png')
strips={'left':[980,910,1056,1180],'right':[1244,910,1320,1180],
        'top':[980,910,1320,986],'bottom':[980,1104,1320,1180]}
for name,b in strips.items():cut(candidate,b).save(OUT/f'qa-mask-{name}-edge.png')
config=Path('D:/work/image/config/image-generation.json')
refs=[imginfo(OUT/'edit-target-1254.png','edit target: exact c09 crop'),imginfo(Path('D:/work/image/designs/gameplay-ui/04-guild.png'),'style only; no UI or object import')]
record={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'useCase':'precise-object-edit',
    'route':'builtin_image_gen','configFile':str(config),'configSha256':sha(config),'configuredTarget':read(config),
    'submittedParameters':{'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False,'model':None,'quality':None,
        'prompt':(OUT/'prompt.txt').read_text(encoding='utf-8')},'actualModel':None,'actualQuality':None,
    'modelEvidence':'Builtin exposed no model/quality selectors and returned no actual model/quality metadata. Config is a target only.',
    'callTimes':{k:tool[k] for k in ['startedAtUtc','returnedAtUtc']},
    'toolSource':{'file':str(gen),'sha256':sha(gen),'fileCreatedAtUtc':datetime.fromtimestamp(gen.stat().st_ctime,timezone.utc).isoformat(),
        'fileModifiedAtUtc':datetime.fromtimestamp(gen.stat().st_mtime,timezone.utc).isoformat()},
    'toolResultFile':str(OUT/'tool-result.json'),'toolResultSha256':sha(OUT/'tool-result.json'),
    'promptFile':str(OUT/'prompt.txt'),'promptSha256':sha(OUT/'prompt.txt'),'references':refs,
    'output':imginfo(raw,'unaltered original returned image; production repair pixel source'),
    'toolCopyByteIdentical':sha(gen)==sha(raw),'sourceTileSha256':target['coreSourceSha256'],
    'resampling':None,'warp':None}
savej(OUT/'generated-original-1254.png.generation.json',record)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'composited_pending_visual_review',
    'sourceCore':imginfo(src,'read-only original 4K candidate'),'sourceHalo':imginfo(src_halo,'read-only original halo candidate'),
    'repairSource':imginfo(raw,'unaltered builtin repair'),'cropInCoreLTRB':list(crop),'maskBoundsInCoreLTRB':list(box),
    'maskDefinition':'300x230 rectangle; cosine inward feather36px; outermost row/column zero; alpha255 beyond36px inward',
    'maskCore':imginfo(OUT/'repair-mask-core4096.png','alpha mask'),'maskCrop':imginfo(OUT/'repair-mask-crop1254.png','same mask in generation crop'),
    'compositing':'per channel round((generated*alpha+original*(255-alpha))/255); integer-grid placement; no resize/registration/warp',
    'resampling':None,'warp':None,'newStructureAdded':False,
    'maskOutsideCoreByteEqual':outerequal,'maskOutsideHaloByteEqual':True,'originalSourceFilesUnchanged':True,
    'westCore230ByteEqual':True,'eastCore230ByteEqual':True,'westHalo230ByteEqual':True,'eastHalo230ByteEqual':True,
    'topAndBottomHaloByteEqual':True,'haloCoreMatches4096':True,'changedPixels':int(changed.sum()),
    'changedBBoxLTRB':[int(sx.min()),int(sy.min()),int(sx.max()+1),int(sy.max()+1)],
    'outputs':[imginfo(core_out,'repaired core candidate'),imginfo(halo_out,'repaired halo candidate')],
    'edgeReviewStrips':strips,'visualReview':None,'formalAccepted':False}
savej(OUT/'repair-record.json',report)
print(json.dumps({'outputs':report['outputs'],'changedBBox':report['changedBBoxLTRB'],'changedPixels':report['changedPixels'],'outsideMaskByteEqual':outerequal}))
