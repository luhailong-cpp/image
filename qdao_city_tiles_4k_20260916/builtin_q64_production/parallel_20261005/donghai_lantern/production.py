"""Scoped native-pixel bookkeeping and guide crops. Never calls a paid API."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
PROJECT=Path('D:/work/image')
DAY=ROOT.parent/'donghai_day/r08_c11'
TILE=ROOT/'r08_c11'
STYLE=PROJECT/'designs/gameplay-ui/04-guild.png'
WEST=PROJECT/'qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_lantern/r08_c08_c09_c10_joint/output_v2/r08_c10.png'
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def item(p,role): return {'file':str(p),'sha256':sha(p),'role':role}
def init():
 for d in ['guides','native','prompts','qa','output']: (TILE/d).mkdir(parents=True,exist_ok=True)
 h=read(ROOT/'handoff.json'); verified=[]
 for e in [h['plan'],h['layout']]+h['baselineCandidates']:
  p=Path(e['file']);s=sha(p);assert s==e['sha256'],str(p);verified.append({'file':str(p),'sha256':s,'expectedSha256':e['sha256'],'matches':True})
 write(ROOT/'source-verification.json',{'checkedAt':now(),'files':verified})
 write(ROOT/'batch-model-check.json',{'checkedAt':now(),'configSnapshot':read(PROJECT/'config/image-generation.json'),'officialSourcesChecked':['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://openai.com/index/introducing-chatgpt-images-2-5/'],'finding':'Sunburst and max confirmed in fetched official pages. Built-in interface has no model or quality selectors. Root configuration unchanged.','actualModel':None,'actualQuality':None})
 out=TILE/'guides/neighbor-tone-native.png';Image.open(WEST).crop((2842,550,4096,1804)).save(out)
 write(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'operation':'unscaled native crop for festival tone only','cropXYXY':[2842,550,4096,1804],'derivedFrom':[item(WEST,'existing west festival candidate')],'finalArt':False})
 status()
def selected_candidate():
 selection_path=ROOT/'current-selection.json'
 if not selection_path.exists():return None
 selection=read(selection_path)
 assert selection['tile']=='r08_c11','Unexpected selected tile'
 for key,size in [('core',(4096,4096)),('extendedContext',(4326,4326))]:
  entry=selection[key];p=Path(entry['file']).resolve()
  assert p.is_relative_to(ROOT.resolve()),'Selected candidate must stay in this task directory'
  assert p.is_file() and sha(p)==entry['sha256'],f'Selected {key} missing or changed: {p}'
  with Image.open(p) as im:
   im.load();assert im.format=='PNG' and im.size==size,f'Invalid selected {key} pixels'
  if entry.get('generationRecord'):
   record=read(entry['generationRecord']);assert record['sha256']==entry['sha256'],'Selected record disagrees with image'
 assert selection.get('completePixelCandidate') is True,'Selection must explicitly identify a complete pixel candidate'
 return selection

def refresh_tile_index(state,selection):
 path=ROOT/'audit/tile-index.json'
 if not path.exists():return
 index=read(path)
 for entry in index['tiles']:
  if entry['id']!='r08_c11':continue
  entry.update(status='complete_pixel_candidate_qa_pending' if selection else 'in_progress',completePixelCandidate=bool(selection),formalAccepted=False,clientAccepted=False,sourceFile=selection['core']['file'] if selection else None,activeOutputDirectory=str(TILE),reason=state['nextAction'])
  if selection:
   entry.update(expectedSha256=selection['core']['sha256'],actualSha256=selection['core']['sha256'],shaMatches=True,actualPixels=[4096,4096],fullDecode=True,selectionFile=str(ROOT/'current-selection.json'),qaStatus=selection['qaStatus'],phase=state['phase'],extendedContext=selection['extendedContext'])
 index['updatedAtUtc']=state['updatedAtUtc']
 index['counts'].update(existingCompletePixelCandidates=state['baselineCompletePixelCandidates'],newCompletePixelCandidates=state['newCompletePixelCandidates'],completePixelCandidates=state['completePixelCandidates'],inProgress=0 if selection else 1,qaOrRepairInProgress=1 if selection else 0,missing=state['missingTiles'],formalAccepted=0,clientAccepted=0)
 index.update(wholeCityComplete=False,runtimePublished=False,currentSelectionFile=str(ROOT/'current-selection.json') if selection else None)
 write(path,index)

def status():
 if (ROOT/'current-candidates.json').exists():
  from publish_candidates import status as registry_status
  return registry_status()
 natives=sorted((TILE/'native').glob('r??_c??.png'))
 day=sorted((DAY/'native').glob('r??_c??.png'))
 h=read(ROOT/'handoff.json');selection=selected_candidate();baseline=len(h['baselineCandidates']);new_count=int(selection is not None)
 phase=selection.get('phase','candidate_qa_pending') if selection else ('native_expansion_in_progress' if natives else 'preparing_exact_day_geometry_input')
 next_action=selection.get('nextAction','Review selected candidate internal seams and shared edges.') if selection else 'Convert each actual day native geometry patch to matching festival appearance with exact west and generated-neighbor context; no independent geometry substitution.'
 state={'appearance':'donghai_lantern','title':'05 渔村元宵地图','updatedAtUtc':now(),'targetCityPixels':[65536,65536],'targetTiles':256,'targetTilePixels':[4096,4096],'baselineCompletePixelCandidates':baseline,'newCompletePixelCandidates':new_count,'completePixelCandidates':baseline+new_count,'missingTiles':256-baseline-new_count-(0 if selection else 1),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'activeTile':'r08_c11','activeGlobalRectXYWH':[40960,28672,4096,4096],'nativeCorePixels':1024,'nativeHaloPixels':115,'nativePatchesSaved':len(natives),'nativePatchesRequiredForActiveTile':16,'fragmentsCountAsTiles':False,'dayGeometryPatchesAvailable':len(day),'phase':phase,'nextAction':next_action,'currentSelectionFile':str(ROOT/'current-selection.json') if selection else None,'currentCompleteCandidate':selection['core'] if selection else None,'qaStatus':selection['qaStatus'] if selection else 'not_ready','sharedGeometryContract':str(ROOT/'audit/shared-geometry-contract.json'),'baselineVerification':str(ROOT/'source-verification.json'),'nativeSourceVerification':str(ROOT/'audit/native-source-verification.json')}
 preview=Image.new('RGB',(2048,1024),(38,49,58));draw=ImageDraw.Draw(preview)
 derived=[]
 for i,e in enumerate(h['baselineCandidates']):
  assert sha(e['file'])==e['sha256'],'Baseline source changed'
  with Image.open(e['file']) as im:
   im.load();assert im.size==(4096,4096),'Baseline is not a complete 4K candidate'
   preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),(i*512,0))
  derived.append(item(e['file'],'existing read-only 4K candidate'))
 if selection:
  with Image.open(selection['core']['file']) as im:preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),(1536,0))
  derived.append(item(selection['core']['file'],'selected current complete 4K pixel candidate; QA pending'))
 else:
  for p in natives:
   r,c=map(int,(p.stem[1:3],p.stem[5:7]));preview.paste(Image.open(p).crop((115,115,1139,1139)).resize((128,128),Image.Resampling.LANCZOS),(1536+(c-1)*128,(r-1)*128))
   derived.append(item(p,'native fragment; not a completed tile'))
 draw.text((15,540),'Existing r08_c08 - c10 | Selected current r08_c11 candidate' if selection else 'Existing r08_c08 - c10 | Active r08_c11 fragments (dark = missing)',fill='white')
 draw.text((15,565),f'Complete pixel candidates: {baseline+new_count}/256 ({baseline} baseline + {new_count} new) | Native fragments: {len(natives)}/16 | Formal accepted: 0/256',fill='white')
 draw.text((15,590),f'Phase: {phase} | Missing tiles: {state["missingTiles"]} | Client acceptance: pending',fill='white')
 draw.text((15,615),'Overview only, downscaled for inspection; not final art or native-resolution seam QA.',fill='white')
 preview.save(ROOT/'current-preview.png')
 write(ROOT/'current-preview.png.generation.json',{'file':str(ROOT/'current-preview.png'),'sha256':sha(ROOT/'current-preview.png'),'operation':'downscaled placement preview of authoritative selected candidate; fragments shown only when no candidate is selected','selectionFile':str(ROOT/'current-selection.json') if selection else None,'derivedFrom':derived,'finalArt':False})
 write(ROOT/'current-work.json',state);write(ROOT/'progress.json',state);refresh_tile_index(state,selection)
def prepare(r,c):
 name=f'r{r:02}_c{c:02}';src=DAY/'native'/f'{name}.png';record=Path(str(src)+'.generation.json')
 assert src.exists() and record.exists(),'Exact day native pixels and provenance not ready'
 s=read(record);assert sha(src)==s['sha256'],'Day source changed'
 im=Image.open(src).convert('RGB');assert im.size==(1254,1254),im.size
 ox=(c-1)*1024;oy=(r-1)*1024;geometry=item(src,'exact native day geometry; preserve all silhouettes, paths, structures and shadows')
 g=im.copy();context=[]
 if c==1:
  y0=max(0,oy-115);y1=min(4096,oy+1139)
  g.paste(Image.open(WEST).crop((3981,y0,4096,y1)),(0,y0-(oy-115)))
  context.append({**item(WEST,'exact existing west festival interior pixels'),'sourceCropXYXY':[3981,y0,4096,y1],'pasteXY':[0,y0-(oy-115)],'resized':False})
 for rr,cc in [(r-1,c-1),(r-1,c),(r-1,c+1),(r,c-1)]:
  p=TILE/'native'/f'r{rr:02}_c{cc:02}.png'
  if not p.exists():continue
  px=(cc-1)*1024;py=(rr-1)*1024;x0=max(ox,px);y0=max(oy,py);x1=min(ox+1254,px+1254);y1=min(oy+1254,py+1254)
  if x1>x0 and y1>y0:
   crop=(x0-px,y0-py,x1-px,y1-py);paste=(x0-ox,y0-oy)
   g.paste(Image.open(p).crop(crop),paste);context.append({**item(p,'exact generated festival overlap'),'sourceCropXYXY':list(crop),'pasteXY':list(paste),'resized':False})
 out=TILE/'guides'/f'{name}.png';g.save(out)
 write(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'operation':'native geometry copy plus exact existing festival context; no resizing','derivedFrom':[geometry]+context,'globalRectXYWH':[40845+ox,28557+oy,1254,1254],'allowedInFinal':False,'context':context})
 refs=[geometry,item(out,'edit target: day geometry with exact already-festival neighbor strips; keep crop fixed'),item(STYLE,'user-confirmed primary art style; no UI or text from it'),item(TILE/'guides/neighbor-tone-native.png','native festival tone sample; no geometry transfer')]
 prompt=f'''Use case: lighting-weather.
Asset: 五行奇谈 original Q-style fishing village Lantern Festival map, internal asset donghai_lantern, tile r08_c11 native fragment {name}.
Image 1 is the exact DAY native geometry. Image 2 is the edit target at the identical 1254-square crop, with existing FESTIVAL neighbor strips overlaid. Image 3 is the user-confirmed PRIMARY ART STYLE. Image 4 is only the existing neighboring festival palette and material rendering.
Convert the remaining DAY appearance in image 2 into the bright Lantern Festival appearance, joining the already-festival edge strips seamlessly. Preserve image 1 geometry precisely: every leaf cluster outline, paving joint, post, roof tile, wall footprint, entrance, rail, step, silhouette, object scale, camera, occlusion and cast-shadow position. No reframing, zoom, shifting, new buildings, roads or props. Keep all four boundaries at their exact positions. No new lanterns; only existing lanterns may glow.
Style must follow image 3: rounded, full, clean and luminous hand-painted Daoist Q-style, clear forms and restrained fine detail. Palette continuity with image 4: honey-gold and peach highlights, warm cream paving, soft lavender shadows, rich green foliage with delicate warm rim light; preserve native blue roofs. Restrained small warm lights, not heavy orange wash, not dark night. Crisp readable structure, no noise, artificial sharpening, haze, UI, text, logos, border, grid or watermark.
Output a single opaque 1254 by 1254 image, same crop and exact geometry. The central 1024-square is the production core; all 115-pixel margins must continue the same scene. Highest visual completion. Config target is gpt-image-2.5-sunburst/max, but this prose is not a model/quality selector.
Global native window XYWH={[40845+ox,28557+oy,1254,1254]}; core XYWH={[40960+ox,28672+oy,1024,1024]}. Do not draw coordinate labels.'''
 pp=TILE/'prompts'/f'{name}.txt';pp.write_text(prompt,encoding='utf-8')
 write(TILE/'prompts'/f'{name}.references.json',refs)
 args={'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False}
 write(TILE/'prompts'/f'{name}.request.json',args)
 print(json.dumps(args,ensure_ascii=False))
def record(name,src):
 src=Path(src);out=TILE/'native'/f'{name}.png';assert not out.exists(),out
 im=Image.open(src);im.load();assert im.size==(1254,1254),im.size
 shutil.copyfile(src,out);req=read(TILE/'prompts'/f'{name}.request.json');refs=read(TILE/'prompts'/f'{name}.references.json')
 write(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool; neither selectors nor actual model/quality metadata disclosed.','evidence':{'toolResultSourcePath':str(src),'sha256':sha(src)},'prompt':str(TILE/'prompts'/f'{name}.txt'),'references':refs,'resizedAfterGeneration':False,'role':'1024 core with 115-pixel context; fragment is not a 4K tile','geometryMatchedTo':refs[0],'visualQA':'pending'})
 status();print(json.dumps({'file':str(out),'sha256':sha(out),'size':im.size}))
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='init':init()
 elif cmd=='status':status()
 elif cmd=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
 elif cmd=='record':record(sys.argv[2],sys.argv[3])
