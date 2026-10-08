from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;T=O.parent.parent;R=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,v):
 with (O/n).open('x',encoding='utf8') as f: json.dump(v,f,ensure_ascii=False,indent=2)
ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha',required=True);ap.add_argument('--prospective-right');ap.add_argument('--prospective-right-sha');a=ap.parse_args()
cpf=T/'source-checkpoint.json';assert sha(cpf)==a.checkpoint_sha
cp=read(cpf);fr=cp['fragment'];lr=cp['coupledNeighbors']['r08_c09']
for ref in [fr,lr]:assert sha(ref['file'])==ref['sha256']
assert fr['tileLocalLTRB']==[0,0,4096,4096]
ctx=Image.new('RGBA',(1254,1254));ctx.paste(Image.open(lr['file']).convert('RGBA').crop((3981,909,4096,2163)),(0,0));ctx.paste(Image.open(fr['file']).convert('RGBA').crop((0,909,1139,2163)),(115,0))
prospective=None
if a.prospective_right:
 p=Path(a.prospective_right);assert sha(p)==a.prospective_right_sha
 source=Image.open(p).convert('RGBA');assert source.size==(1254,1254)
 ctx.paste(source.crop((0,0,230,1254)),(1024,0))
 prospective={**info(p),'role':'prospective native right230 context including its returned upper/lower overlaps; not root committed nor formally accepted','cropLTRB':[0,0,230,1254],'pasteXY':[1024,0],'tileLocalCropLTRB':[909,909,2163,2163],'formalAccepted':False}
known=np.asarray(ctx)[:,:,3]==255;expected=np.ones((1254,1254),bool);expected[230:1024,115:1024]=False
assert np.array_equal(known,expected),'Wait until top/right accepted; inspect unexpected ownership before generating'
assert sha(cpf)==a.checkpoint_sha
ctx.save(O/'context.png');ctx.save(O/'original-context.png')
master=R/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
gb=[36749,29581,38003,30835];box=[-115,909,1139,2163]
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in gb)).save(O/'layout-reference-only.png')
style=R/'designs/gameplay-ui/04-guild.png';refs=[O/'context.png',O/'layout-reference-only.png',style]
prompt='''Use case: precise-object-edit. Complete ONLY the single transparent rectangular hole in image1, keeping the exact native1254x1254 framing. The finished real surrounding map pixels on all FOUR sides are authoritative: left115, top230, right230 and bottom230 pixels. The missing middle spans x115..1023 and y230..1023. It is not a physical rectangle or a stone joint. Preserve every existing contour endpoint, band width, stone-plane color, texture scale and tangent direction in the opaque context.
Continue the broad curved warm ivory ring and the existing quiet gray stone slabs through the missing area so every contour meets all four native sides. A broad diagonal/radial ivory divider is part of the canonical stone layout; derive its exact endpoints from the actual native context. Keep the same connected gray slab equally gray as its visible native top/bottom pieces. Do not bleach it to cream, invent a new seam, narrow a border, change curvature to fit a new composition, add carvings to quiet slabs or introduce extra objects.
Image2 is a low-resolution canonical LOCATION reference of this exact crop, for broad stone placement only. Never enlarge or copy its pixels into the finished crop. Actual precise geometry, material colors and local texture come from image1. Image3 is the approved primary STYLE reference: bright clean rounded Daoist fantasy Q-version hand painting, ivory, jade and restrained warm gold. Apply its polished gentle shading; do not import its UI, letters, characters, frames or emblems. Existing map finish in image1 remains the material anchor.
The new area must have restrained low-contrast native texture, continuous into all four sides without rectangular brightness steps. No cracks, speckles, grunge, extra veins, overdone cloudy texture or blurred enlarged detail. Keep every opaque area unchanged; this is one missing local middle region, not a global redraw. No rescaling, zoom, rotation, camera change, text, watermark or border. Return only the completed opaque1254-square game map crop with the highest finish available through the host.'''
(O/'prompt.txt').write_text(prompt,encoding='utf8')
write('source-checkpoint-snapshot.json',cp)
req={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r02_c01','tile':'r08_c10','globalCropLTRB':gb,'tileLocalCropLTRB':box,'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'configSnapshot':read(R/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None}
write('request.json',req)
write('preparation.json',{'sourceCheckpoint':info(O/'source-checkpoint-snapshot.json'),'currentCheckpointShaAtFreeze':a.checkpoint_sha,'nativeInputs':[{**fr,'role':'real top230/right230/bottom230','cropLTRB':[0,909,1139,2163],'pasteXY':[115,0]},{**lr,'role':'real left115','cropLTRB':[3981,909,4096,2163],'pasteXY':[0,0]}]+([prospective] if prospective else []),'references':[{**info(p),'role':role} for p,role in zip(refs,['native edit target with exactly one missing middle','location only; forbidden final pixels','approved primary style'])],'master':info(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'allWritesConfinedTo':str(O),'formalAccepted':False,'prospectiveContextRequiresLaterPixelVerification':prospective is not None})
for n in ['context.png','original-context.png','layout-reference-only.png']:
 write(n+'.generation.json',{**info(O/n),'derivedFrom':[fr,lr]+([prospective] if prospective else []) if n!='layout-reference-only.png' else [info(master)],'operation':'Exact native context crop' if n!='layout-reference-only.png' else 'Location-only canonical crop; prohibited final pixels','newModelCalls':0,'nativeScale':1 if n!='layout-reference-only.png' else None})
print(json.dumps({'version':cp['version'],'missingPixels':req['missingPixels'],'request':info(O/'request.json')}))
