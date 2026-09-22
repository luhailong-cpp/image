"""Direct-source coordinate guides only; never delivery art."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parent;A=next(p for p in P.parents if (p/'config/image-generation.json').exists());R=A/'qdao_city_tiles_4k_20260916';PROD=R/'builtin_q64_production'
OLD=PROD/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return {'file':str(p),'sha256':sha(p),'role':role}
for n in ['references','guides','native','prompts','qa','output']:(P/n).mkdir(exist_ok=True)
plaza=R/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png';master=A/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';bottom=OLD/'r09_c08.png';quad=OLD/'quad-extended-context.png';right=P.parent/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png';design=A/'designs/guild-ui-v2/source/guild-overview.png'
assert sha(bottom)=='082c9b20f605c9ff695acaae423b72903119baeb4d5dbc475343552020fafdc2'
assert sha(plaza)=='21a40f32316a0d77e411510b71d8dc80a4ace8c4b0e4605291ee060b1aeccf98'
box=[1258.4375,1258.4375,2069.5625,2069.5625]
canvas=Image.open(plaza).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=box)
bottomctx=Image.open(quad).convert('RGB').crop((4096,0,8422,230))
raw=bottomctx.copy();b=np.array(bottomctx);true=np.array(Image.open(bottom).convert('RGB'))
assert np.array_equal(b[115:,115:4211],true[:115])
bottomctx.paste(Image.open(right).convert('RGB').crop((0,0,115,115)),(4211,115))
raw.save(P/'references/bottom-native-context-before-corner.png');bottomctx.save(P/'references/bottom-native-context.png')
canvas.paste(bottomctx,(0,4096));canvas.save(P/'guides/full-canvas-layout-only.png')
canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(P/'references/region-overview-layout-only.jpg',quality=96)
masterbox=[2677.21875,2677.21875,3082.78125,3082.78125]
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=masterbox).save(P/'references/master-region-layout-only.png')
Image.open(bottom).convert('RGB').crop((1421,0,2675,1254)).save(P/'references/qualified-bottom-native-style.png')
style=P/'references/qualified-bottom-native-style.png'
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'role':'Layout/style inputs only, excluded from delivery/native source counts','tile':'r08_c08','globalCoreLTRB':[28672,28672,32768,32768],'globalExtendedLTRB':[28557,28557,32883,32883],'plazaCoreLTRB':[1280,1280,2048,2048],'plazaExtendedLTRB':box,'masterCoreLTRB':[2688,2688,3072,3072],'masterExtendedLTRB':masterbox,'plazaReference':ref(plaza,'nominal local Q-layout reference; no standalone navigation acceptance'),'masterReference':ref(master,'global roads/buildings/navigation geometry authority'),'bottomCore':ref(bottom,'fixed existing actual neighboring core'),'bottomNativeContext':ref(quad,'original native halo and exact bottom core first115 rows, crop[4096,0,8422,230]'),'bottomRightCornerCore':ref(right,'true r09c09 core top-left115x115 replaces outdated halo only'),'designStyle':ref(design,'confirmed primary drawing/material style, no UI content'),'nativeStyle':ref(style,'unresized crop [1421,0,2675,1254] from fixed bottom core'),'referenceResamplingOnly':True,'finalArtUpscaled':False,'navigationAccepted':False,'neighborConstraints':[{'edge':'bottom','tile':'r09_c08','coreSha256':sha(bottom),'contextPath':str(P/'references/bottom-native-context.png'),'contextSha256':sha(P/'references/bottom-native-context.png'),'newExtendedPasteXY':[0,4096]}],'pendingNeighbors':['r08_c07','r08_c09','r07_c08']}
(P/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
config=json.loads((A/'config/image-generation.json').read_text(encoding='utf-8-sig'))
plan={'schemaVersion':3,'tile':'r08_c08','cityAppearance':'tianyong_festival','status':'direct_source_guides_pending_geometry_review','globalCoreLTRB':record['globalCoreLTRB'],'worldRect':{'x':181.25,'z':150,'width':18.75,'height':18.75},'wholeCityPixels':[65536,65536],'tilePixels':[4096,4096],'nativeGrid':[4,4],'nativePixels':[1254,1254],'core':1024,'halo':115,'overlap':230,'assembledPixels':[4326,4326],'configSnapshot':config,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'layoutRecord':ref(P/'layout-record.json','direct source geometry proof'),'patches':[],'productionAccepted':False,'runtimePublished':False}
for row in range(4):
 for col in range(4):
  ident=f'r{row+1:02d}_c{col+1:02d}';box=[col*1024,row*1024,col*1024+1254,row*1024+1254];guide=P/'guides'/f'{ident}.layout-only.png';canvas.crop(box).save(guide)
  prompt=f'Use case: precise-object-edit. Image 1 is the exact square terrain layout crop to repaint at native1254 x1254 pixels. It is detail {ident} of Tianyong festival tile r08_c08 within a continuous Chinese-fantasy city plaza. Repaint into crisp clean high-definition rounded Q/chibi hand-painted map art while preserving the exact camera, crop, scale, geometry and arrangement from image1. Match every paving-joint position, gray groove, step, existing carving outline and boundary; never move or invent streets, buildings, exits, props or decoration. Develop native smooth bevel shading and fine restrained stone material; do not merely enlarge or sharpen a low-resolution reference. Image2 is an unresized native crop of the fixed neighboring city tile, authoritative for matching cream limestone, subdued golden bevels, cool gray recesses, line weight, lighting and clean material. Image3 is the user-confirmed PRIMARY DRAWING/STYLE reference for rounded refined hand-painted materials and warm ivory/gold finishing only; no UI layout or content may enter the terrain. Preserve current city continuity over any decorative style elements: no text, characters, portraits, panels, frames, badges, extra ornaments, extra cracks, noisy grain, watermarks, transparency or blur. Keep open ground open and preserve the outer115 pixels geometry for adjacent overlap. Output ONLY one opaque1254-square native terrain crop, with no border or collage.'
  if row==3:prompt+=' The bottom230 rows of image1 contain native fixed-neighbor halo/core reference. Follow that bottom geometry and material exactly, especially the actual neighboring core in the last115 rows, and cleanly continue it upward without a visible horizontal transition.'
  promptfile=P/'prompts'/f'{ident}.prompt.txt';promptfile.write_text(prompt,encoding='utf-8')
  plan['patches'].append({'id':ident,'row':row,'column':col,'fullCanvasBox':box,'guide':ref(guide,'layout-only edit target'),'promptFile':str(promptfile),'references':[str(guide),str(style),str(design)],'outputFile':f'native/{ident}.png','status':'pending'})
checks=0
for row in range(4):
 for col in range(4):
  im=np.array(Image.open(P/'guides'/f'r{row+1:02d}_c{col+1:02d}.layout-only.png'))
  if row<3:assert np.array_equal(im[-230:],np.array(Image.open(P/'guides'/f'r{row+2:02d}_c{col+1:02d}.layout-only.png'))[:230]);checks+=1
  if col<3:assert np.array_equal(im[:,-230:],np.array(Image.open(P/'guides'/f'r{row+1:02d}_c{col+2:02d}.layout-only.png'))[:,:230]);checks+=1
plan['guideSharedOverlapChecks']={'count':checks,'allExact':True};(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'tile':'r08_c08','guides':16,'overlapChecks':checks,'bottomSha':sha(bottom),'layoutRecord':str(P/'layout-record.json')}))
