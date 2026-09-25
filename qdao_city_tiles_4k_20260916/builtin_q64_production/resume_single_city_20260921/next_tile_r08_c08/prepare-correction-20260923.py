from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json,hashlib,shutil
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
RUN=P/('correction-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));RUN.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
prev=P/'continuation-20260923T072207062411Z'
shutil.copyfile(prev/'save_new_native.py',RUN/'save_new_native.py')
config=ROOT/'config/image-generation.json'
assert config.exists(),str(config)
(RUN/'config-snapshot.json').write_bytes(config.read_bytes())
write(RUN/'model-capability-snapshot.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','availableParameters':['prompt','referenced_image_paths','num_last_images_to_include'],'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'reason':'Current callable schema has no model, quality or size selectors; host-managed route. Same production batch target unchanged.'})
source=P/'native/r04_c03.v2.png';mat=RUN/'native-ivory-material-reference.png'
Image.open(source).crop((300,300,900,900)).save(mat)
write(RUN/'native-ivory-material-reference.derivation.json',{'file':info(mat),'derivedFrom':info(source),'sourceRecord':info(source.with_name('r04_c03.v2.generation.json')),'operation':'Exact native crop [300,300,900,900], no resize or repaint','role':'Material-only design reference; NOT production pixels'})
style=ROOT/'designs/gameplay-ui/04-guild.png'
descs={
'r03_c01':'Image 1 has an upright curved band of carved ivory tablets at center; preserve every glyph silhouette, block joint and gold/blue outer rings exactly. At far LEFT x=0..95 there is only ONE true horizontal stone joint, at y approximately 770. Above y=740 that narrow far-left ivory slab is uninterrupted. Do not invent a second joint at y=590. Preserve the gold band joint at y=770 and all center tablet boundaries.',
'r03_c02':'Image 1 is a PLAIN BLANK ivory stone field occupying the right 80 percent. The ONLY constructed geometry is the cropped upright concentric curved gray and warm gold rims at the LEFT edge. The wide diagonal branching marks across ivory are stains/mineral veins to REMOVE ENTIRELY, not motifs or carvings. The ivory field must be blank with soft broad shading; zero relief, outlines, ribbons, joints or ornaments.',
'r03_c03':'Image 1 is almost entirely a PLAIN BLANK ivory stone field. The ONLY constructed geometry is a tiny cropped dark blue-gray curved rim at the extreme TOP-RIGHT corner (approximately last 120 pixels of top and first 160 pixels of right edge). Remove every diagonal branching vein. The central and lower field contain ZERO lines, blocks, joints, steps, carvings or ornaments. Do not copy another image composition. Preserve the small dark corner crop exactly.',
'r03_c04':'Image 1 has a cropped huge dark blue-gray oval across the TOP and RIGHT, with its curved rim running from approximately (110,0) to (1254,560). Preserve that exact oval outline, crop and rim geometry. All ivory below/left is a plain BLANK field. Every diagonal branching ivory mark is a stain/mineral vein and must be REMOVED COMPLETELY, not turned into a ribbon or relief. No new joints, glyphs, objects or outlines.',
'r04_c04':'Image 1 is a plain ivory stone field with ONE dark blue-gray oval occupying the middle/right/lower-right, cropped at the right edge. Preserve oval exact size, crop, rim, contour and position. Oval interior is completely blank smooth blue-gray. Near the bottom retain only existing actual diagonal slab joints. All broad branching ivory veins must be removed, not embossed. The guide horizontal paste boundary near y=1024 is NOT an edge: join lighting naturally through it.'}
common=' Use case: precise-object-edit. Asset: one native 1254 x 1254 terrain patch for Tianyong festival tile r08_c08. EDIT IMAGE 1 ONLY. Image 1 is the exact geometry and framing authority, but repaint its low-resolution material into genuinely sharp native detail. Image 2 is a small native ivory MATERIAL COLOR sample only, no scene composition. Image 3 is the confirmed PRIMARY project drawing-style reference, clean bright rounded Q/chibi hand painting only; no UI text, people, symbols or layout from it. Retain image 1 camera, scale, object silhouettes, constructed joints, shadows, and all 115 pixel overlap geometry. Clean warm ivory and warm gold with crisp rounded bevels and broad subtle lighting; calm dark slate blue. Smooth generous hand-painted planes. No flakes, small polygonal paint dabs, mottling, marble veins, microtexture, stippling, grain or cloudy patches. No new cracks, glyphs, decorative relief, architecture, objects, steps, seams or border. No color band at guide paste boundary. One opaque square full-bleed native terrain image, exactly 1254 x 1254; no collage, text, UI or watermark. Do not enlarge or merely sharpen the guide. Output only the first target composition with the specific described geometry.'
for ident,desc in descs.items():
 stem=ident+'.v3';guide=P/'guides'/f'{ident}.layout-only.png';refs=[guide,mat,style]
 request={'prompt':desc+common,'referenced_image_paths':[str(x) for x in refs]}
 write(RUN/f'{stem}.request.json',request)
 pre={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c08','internalPatch':ident,'versionStem':stem,'configSnapshot':json.loads(config.read_text(encoding='utf-8-sig')),'configSnapshotFile':info(RUN/'config-snapshot.json'),'modelCapabilityEvidence':info(RUN/'model-capability-snapshot.json'),'request':info(RUN/f'{stem}.request.json'),'references':[dict(info(x),role=r) for x,r in zip(refs,['geometry-only target','native smooth ivory material only','confirmed primary drawing style only'])],'editBefore':dict(info(guide),layoutRecord=info(P/'layout-record.json')),'actualModel':None,'actualQuality':None,'formalAccepted':False}
 write(RUN/f'{stem}.preflight.json',pre)
write(RUN/'initial-review-findings.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'failedOriginals':{'r03_c01.v2':'Invented extra left paving joint near y590; original only near y770','r03_c02.v2':'Mineral veins converted into relief','r03_c03.v2':'Wrong composition copied material reference','r03_c04.v2':'Mineral veins converted into relief','r04_c03.v2':'Guide-paste horizontal band y1024; diagonal grout abruptly begins there'},'missingNative':['r04_c04'],'scope':'Direct original-pixel viewing, not whole-tile or formal acceptance'})
print(json.dumps({'run':str(RUN)}))
