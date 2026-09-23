"""Independent r08_c09 native-detail preparation, retention, assembly and QA crops."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, re, shutil, sys
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
SESSION=P.parent
ART=P.parents[2]
REPO=ART.parent
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda: datetime.now(timezone.utc).isoformat()

def write(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

def info(p):return {'file':str(Path(p).resolve()),'sha256':sha(p)}

def prepare():
 for name in ('references','guides','native','prompts','requests','qa','output'):(P/name).mkdir(exist_ok=True)
 assert not (P/'plan.json').exists(),'Do not overwrite prepared layout'
 plaza=ART/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
 master=REPO/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
 bottom=SESSION/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
 extended=SESSION/'next_tile_r09_c10/references/latest-left-r09_c09-v6/extended-context.png'
 extended_record=extended.with_name('record.json')
 design=REPO/'designs/guild-ui-v2/source/guild-overview.png'
 assert sha(bottom)=='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
 assert sha(extended)==read(extended_record)['output']['sha256']
 b=Image.open(bottom).convert('RGB');ex=Image.open(extended).convert('RGB')
 assert b.size==(4096,4096) and ex.size==(4326,4326)
 assert np.array_equal(np.array(b),np.array(ex.crop((115,115,4211,4211))))
 plaza_box=[2026.4375,1258.4375,2837.5625,2069.5625]
 master_box=[3061.21875,2677.21875,3466.78125,3082.78125]
 canvas=Image.open(plaza).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=plaza_box)
 master_guide=Image.open(master).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=master_box)
 canvas.save(P/'references/plaza-geometry-layout-only.png')
 master_guide.save(P/'references/master-geometry-layout-only.png')
 constraint=ex.crop((0,0,4326,230));constraint.save(P/'references/bottom-overlap-native.png')
 canvas.paste(constraint,(0,4096));canvas.save(P/'guides/full-canvas-layout-only.png')
 b.thumbnail((1254,1254),Image.Resampling.LANCZOS);b.save(P/'references/bottom-candidate-style-reference.png')
 overview=Image.new('RGB',(2048,1024));overview.paste(master_guide.resize((1024,1024),Image.Resampling.LANCZOS),(0,0));overview.paste(Image.open(P/'references/plaza-geometry-layout-only.png').resize((1024,1024),Image.Resampling.LANCZOS),(1024,0));overview.save(P/'qa/master-left_plaza-right_same-coordinate-preview.png')
 config=read(REPO/'config/image-generation.json');write(P/'config-snapshot.json',config)
 geometry={'createdAtUtc':now(),'role':'layout/reference only; never used as final output pixels','tile':'r08_c09',
  'globalPixelRectXYWH':[32768,28672,4096,4096],'worldRect':{'x':200,'z':150,'width':18.75,'height':18.75},
  'plaza':{**info(plaza),'sourceBoxLTRB':plaza_box},'master':{**info(master),'sourceBoxLTRB':master_box},
  'referenceCanvasPixels':[4326,4326],'referenceResampled':True,'geometryMeaning':'Nominal linear crop transform is established; semantic master/plaza geometry and navigation acceptance remain unestablished.',
  'bottomConstraint':{**info(extended),'record':info(extended_record),'sourceBoxLTRB':[0,0,4326,230],'pasteXY':[0,4096],
     'core':info(bottom),'corePixelsExactEqual':True,'neighborWillNotBeModified':True},
  'otherNeighborConstraints':{'left':'pending r08_c08 production','top':'pending','right':'pending'},
  'resizedArtUsedInFinal':False,'formalAccepted':False}
 write(P/'layout-record.json',geometry)
 shared=[P/'references/bottom-candidate-style-reference.png',design]
 patches=[]
 for row in range(4):
  for col in range(4):
   ident=f'r{row+1:02}_c{col+1:02}';box=[col*1024,row*1024,col*1024+1254,row*1024+1254]
   guide=P/'guides'/f'{ident}.layout-only.png';canvas.crop(box).save(guide)
   prompt=(f'Use case: precise-object-edit. Edit image 1 only: exact terrain crop {ident} of Tianyong festival map tile r08_c09. '
    'Image 1 is the sole geometry authority: keep its camera, crop, scale, every slab joint, rim curve, step count, carving outline, shadow footprint and relative position unchanged. '
    'Image 2 is the selected adjacent map artwork, used only to match clean warm ivory limestone, rounded bevels, soft cream highlights and restrained taupe/gray recesses. '
    'Image 3 is the main confirmed project drawing/material style sample; use its premium clean hand-painted Q/chibi craftsmanship only, never its interface, text, characters, layout or objects. '
    'Repaint image 1 as crisp native-resolution Chinese fantasy Q game terrain. Develop clear sculpted contours and clean smooth stone planes, not grain or enlarged blurry pixels. '
    'Exactly preserve all actual paving divisions and any cloud relief already present in this crop; keep blank panels blank. No new patterns, seams, cracks, decorations, motifs, blocks or objects. '
    'Preserve precise positions in all outer 115 pixels, which overlap the surrounding map; do not rotate, zoom or recompose. '
    'One fully opaque square continuous terrain image. No people, text, UI, frame, grid, collage, watermark, transparency, gritty texture, blur or sharpening halos.')
   promptfile=P/'prompts'/f'{ident}.prompt.txt';promptfile.write_text(prompt,encoding='utf-8')
   refs=[guide,*shared]
   request={'prompt':prompt,'referenced_image_paths':[str(x) for x in refs]}
   write(P/'requests'/f'{ident}.request.json',request)
   write(guide.with_suffix('.derived.json'),{'derivedFrom':[info(plaza),info(extended)],'operation':'Reference-only equal-scale source-box resampling and fixed bottom overlap paste, then 1254 square crop','canvasBoxLTRB':box,'output':info(guide),'notDeliveryArtwork':True,'layoutRecord':info(P/'layout-record.json')})
   patches.append({'id':ident,'row':row,'column':col,'guide':str(guide),'guideSha256':sha(guide),'fullCanvasBox':box,'outputFile':f'native/{ident}.png','promptFile':str(promptfile),'submittedImages':[str(x) for x in refs],'request':str(P/'requests'/f'{ident}.request.json')})
 checks=0
 for row in range(4):
  for col in range(4):
   a=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+1:02}.layout-only.png'))
   if col<3:
    c=np.array(Image.open(P/'guides'/f'r{row+1:02}_c{col+2:02}.layout-only.png'));assert np.array_equal(a[:,-230:],c[:,:230]);checks+=1
   if row<3:
    c=np.array(Image.open(P/'guides'/f'r{row+2:02}_c{col+1:02}.layout-only.png'));assert np.array_equal(a[-230:],c[:230]);checks+=1
 plan={'schemaVersion':3,'tile':{'row':8,'column':9,'worldRect':geometry['worldRect']},'status':'native_generation_prepared_not_accepted','route':'builtin_image_gen',
  'configSnapshot':config,'requestedModel':config['model'],'requestedQuality':config['quality'],'actualModel':None,'actualQuality':None,
  'submittedParameters':{'model':None,'quality':None},'backendModelVerified':False,'wholeCityPixels':[65536,65536],'deliveryTilePixels':[4096,4096],
  'core':1024,'halo':115,'adjacentOverlap':230,'assembledBeforeOuterCrop':[4326,4326],'patches':patches,
  'sharedGuideOverlapChecks':checks,'sharedGuideOverlapExact':True,'layoutRecord':info(P/'layout-record.json'),'formalAccepted':False}
 write(P/'plan.json',plan)
 write(P/'references/derived-records.json',{'references':[{'file':str(P/'references/bottom-candidate-style-reference.png'),'sha256':sha(P/'references/bottom-candidate-style-reference.png'),'derivedFrom':info(bottom),'operation':'1254 maximum-side thumbnail for style only','productionArtwork':False}, {'file':str(design),'sha256':sha(design),'operation':'Unmodified approved designs image used as style input'}]})
 print(json.dumps({'prepared':len(patches),'sharedOverlapChecks':checks,'bottomCoreVerified':True,'directory':str(P)}))

def save(ident):
 plan=read(P/'plan.json');patch=next(x for x in plan['patches'] if x['id']==ident.split('.')[0])
 receiptpath=P/'requests'/f'{ident}.receipt.json';receipt=read(receiptpath)
 assert receipt['request']==read(patch['request'])
 m=re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S);assert m
 src=Path(m.group(1));dst=P/patch['outputFile'];assert not dst.exists()
 with Image.open(src) as im:im.load();dims=list(im.size);mode=im.mode;assert dims==[1254,1254];assert im.format=='PNG'
 shutil.copyfile(src,dst);assert sha(src)==sha(dst)
 refs=[{'path':s,'file':s,'sha256':sha(s),'role':('exact layout edit target' if i==0 else 'selected adjacent Q map material style' if i==1 else 'confirmed designs primary drawing/material style; no UI content')} for i,s in enumerate(receipt['request']['referenced_image_paths'])]
 record={'schemaVersion':4,'file':str(dst),'sha256':sha(dst),'nativeFile':str(dst),'nativeSha256':sha(dst),
 'toolOutputPath':str(src),'toolOutputSha256':sha(src),'toolOutputBytes':src.stat().st_size,'nativePixels':dims,'width':dims[0],'height':dims[1],'format':'PNG','imageMode':mode,
 'createdAtUtc':now(),'generatedAt':None,'observedCompletionAt':receipt['completedAtUtc'],'observedCompletionAtMeaning':'Host-side tool result receipt observation, not exact server generation time',
 'tool':'image_gen.imagegen','route':'builtin_image_gen','configSnapshot':plan['configSnapshot'],'requestedModel':plan['requestedModel'],'requestedQuality':plan['requestedQuality'],
 'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed tool exposes no model/quality selectors and returned no verified backend model, quality, or exact server generation time',
 'promptFile':patch['promptFile'],'promptSha256':sha(patch['promptFile']),'promptTransport':'Exact prompt field of retained request JSON',
 'prompt':{'file':patch['promptFile'],'sha256':sha(patch['promptFile'])},'submittedImages':refs,'references':refs,'selectedTargetImageOneBased':1,
 'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':receipt['request']['referenced_image_paths'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},
 'evidence':info(receiptpath),'editBefore':{'image':refs[0],'record':info(Path(patch['guide']).with_suffix('.derived.json'))},
 'resampled':False,'finalArtUpscaled':False,'accepted':False,'runtimePublished':False}
 write(dst.with_suffix('.record.json'),record)
 write(dst.with_suffix('.png.generation.json'),record)
 print(json.dumps({'id':ident,'source':str(src),'sha256':sha(dst),'dimensions':dims,'nativeRetained':True}))

def assemble():
 plan=read(P/'plan.json');assert not (P/'output/r08_c09.candidate.png').exists()
 helper=ART/'builtin_q64_production/tianyong_festival/r09_c09/assemble_builtin.py'
 spec=importlib.util.spec_from_file_location('native_assembly_helper',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.HELPERS=REPO/'tianyong_festival_hd_20260910/seam_helpers.py';seam=m.load_seam_helper()
 rows=[];entries=[];metrics=[]
 for row in range(4):
  sources=[]
  for col in range(4):
   patch=next(x for x in plan['patches'] if x['row']==row and x['column']==col);f=P/patch['outputFile'];r=f.with_suffix('.record.json');rec=read(r)
   assert sha(f)==rec['nativeSha256']==rec['toolOutputSha256']==sha(rec['toolOutputPath'])
   assert sha(rec['promptFile'])==rec['promptSha256'];assert all(sha(x['path'])==x['sha256'] for x in rec['submittedImages'])
   assert [x['path'] for x in rec['submittedImages']]==patch['submittedImages']
   assert not rec['resampled'] and not rec['finalArtUpscaled']
   im=Image.open(f);im.load();assert im.size==(1254,1254)
   sources.append(np.array(im.convert('RGB')));entries.append({'id':patch['id'],**info(f),'pixels':[1254,1254],'record':info(r)})
  strip=sources[0]
  for col in range(1,4):strip,metric=m.append_patch(strip,sources[col],seam,f'row{row+1}_join{col}');metrics.append(metric)
  assert strip.shape==(1254,4326,3);rows.append(strip)
 combined=rows[0].transpose(1,0,2)
 for row in range(1,4):combined,metric=m.append_patch(combined,rows[row].transpose(1,0,2),seam,f'row_join{row}');metrics.append(metric)
 ex=Image.fromarray(combined.transpose(1,0,2));assert ex.size==(4326,4326)
 tile=ex.crop((115,115,4211,4211));ex.save(P/'output/extended-context.png');tile.save(P/'output/r08_c09.candidate.png')
 rec={'createdAtUtc':now(),'tile':'r08_c09','role':'candidate_not_production_delivery','sources':entries,'sourceCount':16,
 'globalPixelRectXYWH':[32768,28672,4096,4096],'worldRect':plan['tile']['worldRect'],'output':info(P/'output/r08_c09.candidate.png'),
 'extendedContext':info(P/'output/extended-context.png'),'composition':{'method':'Minimum error overlap seam with 2px local feather','overlapPixels':230,'sourceResampling':False,'guidePixelsUsedInOutput':False,'upscaled':False,'outerCropPixels':115},
 'helper':info(helper),'seamHelper':info(m.HELPERS),'metrics':metrics,'actualModel':None,'actualQuality':None,'formalAccepted':False,'runtimePublished':False}
 write(P/'output/assembly.json',rec);print(json.dumps({'candidate':rec['output'],'sourceCount':16}))

def qa():
 tile=Image.open(P/'output/r08_c09.candidate.png').convert('RGB');bottom=Image.open(read(P/'layout-record.json')['bottomConstraint']['core']['file']).convert('RGB')
 tile.resize((1024,1024),Image.Resampling.LANCZOS).save(P/'qa/overview-preview-only.png');records=[]
 def save_image(im,name,parts):
  file=P/'qa'/name;assert not file.exists();im.save(file);records.append({**info(file),'pixels':list(im.size),'parts':parts,'resampled':False})
 for axis in ('vertical','horizontal'):
  for idx in range(1,4):
   out=Image.new('RGB',(920,1024) if axis=='vertical' else (1024,920));parts=[]
   for seg in range(4):
    c=idx*1024;box=[c-115,seg*1024,c+115,(seg+1)*1024] if axis=='vertical' else [seg*1024,c-115,(seg+1)*1024,c+115]
    xy=[seg*230,0] if axis=='vertical' else [0,seg*230];out.paste(tile.crop(box),xy);parts.append({'boxLTRB':box,'pasteXY':xy})
   save_image(out,f'internal-{axis}-{idx}-100pct.png',parts)
 out=Image.new('RGB',(690,690));parts=[]
 for row in range(1,4):
  for col in range(1,4):
   box=[col*1024-115,row*1024-115,col*1024+115,row*1024+115];xy=[(col-1)*230,(row-1)*230];out.paste(tile.crop(box),xy);parts.append({'boxLTRB':box,'pasteXY':xy})
 save_image(out,'internal-nine-junctions-100pct.png',parts)
 out=Image.new('RGB',(1024,920));parts=[]
 for seg in range(4):
  x=seg*1024;patch=Image.new('RGB',(1024,230));patch.paste(tile.crop((x,3981,x+1024,4096)),(0,0));patch.paste(bottom.crop((x,0,x+1024,115)),(0,115));out.paste(patch,(0,seg*230));parts.append({'columnInterval':[x,x+1024],'boundaryY':seg*230+115})
 save_image(out,'external-bottom-r09_c09-100pct.png',parts)
 write(P/'qa/evidence-index.json',{'createdAtUtc':now(),'candidate':info(P/'output/r08_c09.candidate.png'),'assembly':info(P/'output/assembly.json'),'boards':records,'internalFullSeamsCovered':6,'internalJunctionsCovered':9,'bottomFullEdgeCovered':True,'otherEdges':'pending_neighbor_candidates','visualReviewPerformed':False,'formalAccepted':False})
 print(json.dumps({'boards':len(records),'directory':str(P/'qa')}))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','save','requests','assemble','qa']);ap.add_argument('ids',nargs='*');args=ap.parse_args()
 if args.mode=='prepare':prepare()
 elif args.mode=='save':
  for ident in args.ids:save(ident)
 elif args.mode=='requests':print(json.dumps([{'id':x.get('versionStem',x['id']),'request':read(x['request'])} for x in read(P/'plan.json')['patches']]))
 elif args.mode=='assemble':assemble()
 else:qa()
