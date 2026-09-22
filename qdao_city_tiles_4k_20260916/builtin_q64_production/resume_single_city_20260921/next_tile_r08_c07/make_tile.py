from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,sys,shutil,importlib.util
import numpy as np
P=Path(__file__).resolve().parent
R=P.parents[3]
V=P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def init():
 assert not (P/'plan.json').exists()
 for n in ['references','guides','requests','native','prompts','qa','output']:(P/n).mkdir(exist_ok=True)
 plaza=R/'qdao_city_tiles_4k_20260916/builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
 master=R/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
 assert sha(plaza)=='21a40f32316a0d77e411510b71d8dc80a4ace8c4b0e4605291ee060b1aeccf98'
 bottom=V/'r09_c07.png';ext=V/'quad-extended-context.png'
 extim=Image.open(ext).convert('RGB');bottomim=Image.open(bottom).convert('RGB')
 assert np.array_equal(np.array(extim.crop((115,115,4211,4211))),np.array(bottomim))
 full=Image.open(plaza).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=(490.4375,1258.4375,1301.5625,2069.5625))
 full.paste(extim.crop((0,0,4326,230)),(0,4096));full.save(P/'guides/full-layout-reference-only.png')
 full.resize((1254,1254),Image.Resampling.LANCZOS).save(P/'references/full-layout-reference-only.png')
 source=Image.open(master).convert('RGB').crop((2304,2688,2688,3072));source.save(P/'references/master-layout-384-reference-only.png')
 style=P.parent/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
 Image.open(style).convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(P/'references/q-style-only.png')
 design=R/'designs/guild-ui-v2/source/guild-overview.png'
 layout={'tile':'r08_c07','sourceMaster':{'path':str(master),'sha256':sha(master),'coreLTRB':[2304,2688,2688,3072]},'plazaReference':{'path':str(plaza),'sha256':sha(plaza),'extendedCropLTRB':[490.4375,1258.4375,1301.5625,2069.5625]},'bottomCore':{'path':str(bottom),'sha256':sha(bottom)},'bottomHalo':{'path':str(ext),'sha256':sha(ext),'cropLTRB':[0,0,4326,230],'pasteXY':[0,4096],'corePixelsVerifiedIdentical':True},'styleSource':{'path':str(style),'sha256':sha(style),'role':'Q painterly material reference only'},'designsStyle':{'path':str(design),'sha256':sha(design),'role':'approved painting/material/finish only; no UI or motif imports'},'guideIsProductionArt':False,'nativeDetailSource':False,'guideResized':True,'globalCoreLTRB':[24576,28672,28672,32768]}
 write(P/'layout-record.json',layout)
 plan={'tile':'r08_c07','requestedConfigSnapshot':read(R/'config/image-generation.json'),'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'route':'builtin_image_gen','nativeGrid':[4,4],'nativePixels':[1254,1254],'core':1024,'halo':115,'overlap':230,'generationOrder':'bottom row to top row, left to right; fixed old bottom halo priority','globalCoreLTRB':[24576,28672,28672,32768],'formalAccepted':False,'patches':[{'id':f'r{r+1:02}_c{c+1:02}','row':r,'col':c,'status':'pending'} for r in range(3,-1,-1) for c in range(4)]}
 write(P/'plan.json',plan)
 write(P/'capability-check.json',{'checkedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','exposedArguments':['prompt','referenced_image_paths','num_last_images_to_include'],'modelSelector':False,'qualitySelector':False,'sizeSelector':False,'actualModel':None,'actualQuality':None,'officialPagesRead':['https://openai.com/index/introducing-chatgpt-images-2-5/','https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'],'officialAvailabilityDoesNotProvePerCallModel':True,'configurationSnapshot':plan['requestedConfigSnapshot']})
 print(json.dumps(layout))
def prepare(ident):
 plan=read(P/'plan.json');p=next(x for x in plan['patches'] if x['id']==ident);r=p['row'];c=p['col']
 out=P/'guides'/f'{ident}.layout-context.png';assert not out.exists()
 im=Image.open(P/'guides/full-layout-reference-only.png').convert('RGB').crop((c*1024,r*1024,c*1024+1254,r*1024+1254))
 derived=[{'path':str(P/'guides/full-layout-reference-only.png'),'sha256':sha(P/'guides/full-layout-reference-only.png'),'cropLTRB':[c*1024,r*1024,c*1024+1254,r*1024+1254]}]
 if c>0:
  f=Path(next(x for x in plan['patches'] if x['id']==f'r{r+1:02}_c{c:02}')['native']);assert f.exists();im.paste(Image.open(f).convert('RGB').crop((1024,0,1254,1254)),(0,0));derived.append({'path':str(f),'sha256':sha(f),'cropLTRB':[1024,0,1254,1254],'pasteXY':[0,0]})
 if r<3:
  f=Path(next(x for x in plan['patches'] if x['id']==f'r{r+2:02}_c{c+1:02}')['native']);assert f.exists();im.paste(Image.open(f).convert('RGB').crop((0,0,1254,230)),(0,1024));derived.append({'path':str(f),'sha256':sha(f),'cropLTRB':[0,0,1254,230],'pasteXY':[0,1024]})
 else:
  f=V/'quad-extended-context.png';im.paste(Image.open(f).convert('RGB').crop((c*1024,0,c*1024+1254,230)),(0,1024));derived.append({'path':str(f),'sha256':sha(f),'cropLTRB':[c*1024,0,c*1024+1254,230],'pasteXY':[0,1024]})
 im.save(out)
 prompt=f'''Use case: precise-object-edit. Create exactly ONE square 1254x1254 native-resolution finished terrain crop, editing image 1 ONLY. This is patch {ident} within map tile r08_c07 of Tianyong festival city, a fixed continuous Chinese fantasy game map. Image 1 is the exact crop and immutable geometry guide, including 230-pixel real neighboring overlap along its bottom and (where present) left edges. Image 2 is the whole tile layout reference ONLY; do not zoom out or substitute that whole tile. Image 3 is the Q/chibi stone material and rendering reference ONLY. Image 4 is the user-approved designs painting reference ONLY: emulate clean hand-painted volume, round polished shapes and restrained warm cream/gold shading, absolutely do not draw its UI, text, icons, decorative extras or characters.
Repaint image 1 with crisp native hand-painted detail and clean rounded stonework while preserving its exact camera angle, crop, scale, perspective, positions, curved ring boundaries, cloud carving silhouettes, and every existing structural paving joint. Do not thicken, move, merge, split, add or remove paving slabs; keep all road and navigation areas open. Preserve fixed borders and crossing positions, especially in the 230-pixel existing neighbor overlap. Match image 3's clean restrained mineral shading and edge sharpness. Remove excessive tiny cracks/noise of the old layout guide, but preserve major structural outlines. Do not invent cracks, grain, scratches, vegetation, props, lanterns, steps or architecture. Do not turn ring paving ornaments into stairs. No blur, no sharpen halos, no thick white rim, no dense texture, no UI, no text, no frame. Highest visual finish available. Output only the exact image-1 terrain crop, fully opaque. Native details must be newly painted; do not merely enlarge or sharpen the guide.'''
 prompt+=' The input guide is a composite: visible straight rectangular material boundaries at x=230 or y=1024 are NOT scene geometry. Paint continuously through those artificial rectangle boundaries; use the clean smooth restrained shading of the bottom neighbor for the whole same stone surface. Very subtle broad tones, no mottled marble watercolor patches, no cloudy surface pattern, no white frosting. Preserve real paving divisions only.'
 prompt=f'''Use case: precise-object-edit. Edit image 1 ONLY and output one opaque square native 1254x1254 terrain crop. This is patch {ident} of Tianyong city tile r08_c07. Image 1 is a composite geometric guide, not the desired material. Keep exactly the same stone boundaries, carved silhouettes, curved or straight structural joints, crop, scale and top-down oblique camera. Image 2 is context layout ONLY; never output the whole layout. Image 3 is the exact clean Q/chibi material reference. Image 4 is the approved designs painting reference ONLY, no UI/text/objects imported.
Replace ALL the old guide surfaces with the clean image-3 painting finish. Remove ALL flake/mottle/crackle/marble/grain pattern everywhere, especially dark gray slabs. Render the entire image in one unified clean premium Q/chibi hand-painted stone finish: very smooth broad sparse tonal gradients, gently warm ivory, quiet stone faces, crisp restrained rounded bevels, soft warm shadows. Do not follow the old guide material. Visible straight rectangular material transitions at x=230 or y=1024 are guide paste artifacts, not geometry: erase these material transitions, paint one continuous stone face across them while retaining only real major stone boundaries. No new slab divisions, no cracks, noise, texture, speckles, flakes, veins, white frosting, plastic shine or blur. Keep existing gold strips but remove sparkly/mottled texture. Preserve original road layout and empty traversable regions, no objects or characters, no actual stairs invented from paving ornaments. Do not move structural lines. Generate crisp native rendered edges and volumes, not enlarged guide pixels. Return only the exact image-1 crop with continuous uniform clean materials, no frame, no text.'''
 promptfile=P/'prompts'/f'{ident}.prompt.txt';promptfile.write_text(prompt,encoding='utf-8')
 refs=[str(out),str(P/'references/full-layout-reference-only.png'),str(P/'native/r04_c01.v2.png') if (P/'native/r04_c01.v2.png').exists() else str(P/'references/q-style-only.png'),str(R/'designs/guild-ui-v2/source/guild-overview.png')]
 request={'prompt':prompt,'referenced_image_paths':refs};write(P/'requests'/f'{ident}.request.json',request)
 write(P/'guides'/f'{ident}.derivation.json',{'role':'input reference only, excluded from production detail count','derivedFrom':derived,'fullGuideUpscaledForReferenceOnly':True})
 p['promptFile']=str(promptfile);p['submittedImages']=refs;p['guide']=str(out);p['status']='prepared';write(P/'plan.json',plan);print(json.dumps(request))
def ingest(ident,src,response):
 plan=read(P/'plan.json');p=next(x for x in plan['patches'] if x['id']==ident);src=Path(src);stem=p.get('selectedStem',ident);dst=P/'native'/f'{stem}.png';assert not dst.exists()
 im=Image.open(src);im.load();assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 shutil.copyfile(src,dst);rec={'schemaVersion':3,'file':str(dst),'sha256':sha(dst),'nativeWidth':im.width,'nativeHeight':im.height,'format':im.format,'mode':im.mode,'route':'builtin','tool':'image_gen.imagegen','generatedAt':None,'observedCompletionAt':read(response)['observedCompletionAt'],'timestampSemantics':'tool completion observed by client, server generation time not disclosed','configSnapshot':plan['requestedConfigSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'host managed; tool exposes no model/quality selectors and returned no verifiable model/quality metadata','evidence':{'toolResponse':str(Path(response).resolve()),'sha256':sha(response),'request':str(P/'requests'/f'{ident}.request.json'),'requestSha256':sha(P/'requests'/f'{ident}.request.json')},'promptFile':p['promptFile'],'promptSha256':sha(p['promptFile']),'references':[{'path':f,'sha256':sha(f)} for f in p['submittedImages']],'toolOutputPath':str(src),'toolOutputSha256':sha(src),'rawBytesPreserved':True,'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False}
 request=Path(p.get('requestFile',P/'requests'/f'{ident}.request.json'));rec['evidence']['request']=str(request);rec['evidence']['requestSha256']=sha(request)
 write(P/'native'/f'{stem}.record.json',rec);p['status']='native_saved_pending_qa';p['native']=str(dst);p['record']=str(P/'native'/f'{stem}.record.json');p['sha256']=sha(dst);write(P/'plan.json',plan);print(json.dumps({'id':ident,'file':str(dst),'sha256':sha(dst),'nativePixels':im.size}))
if __name__=='__main__':
 if sys.argv[1]=='init':init()
 elif sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='ingest':ingest(*sys.argv[2:])
