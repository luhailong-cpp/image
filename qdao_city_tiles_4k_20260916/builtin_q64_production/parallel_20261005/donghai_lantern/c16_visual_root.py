"""Frozen-baseline visual repair, native AI sources and exact masked assembly.

No resizing, geometry warp, texture blur, sibling writes or automatic acceptance.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
T=ROOT/'r08_c16'; BASE=T/'repairs/approved-sync'; B=T/'repairs/visual-finish-root'
CORE=BASE/'output/r08_c16.png'; EXT=BASE/'output/extended-context.png'
CS='7d821e83179cae126dd4e0f1be7f6b83f6a762bfe7b0f0caa4bfa3ec8de0bb22'
ES='7a6c1c38892ca9a35f3b433b27b960660af00d9415df37f2f72304efe52a4cb6'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
TASKS={
 'left-water':{'rect':[200,2957,1454,4211],'roi':[350,3710,1421,4211],'feather':[80,100,80,0], 'note':'Only repair the irregular vertical cyan/violet colour cuts in the water and the narrow reflected waterline below the hull, especially image x around 385 and 755. These continue across a single continuous water surface. Connect the existing blue reflection gently and continuously while preserving the hull silhouette, lantern placement and all material boundaries exactly. Keep wood and lantern unchanged; no new object, ripple or light. This repair does not change any geometric fold, only the abruptly pasted colours.'},
 'hull-band':{'rect':[1421,2360,2675,3614],'roi':[1570,2640,2510,3340],'feather':[128,128,128,128], 'note':'Repair the irregular vertical cyan/purple paint boundaries at image x around 400 and 820, across the blue wooden board and curved gold/brown rim. They are pasted lighting seams, not board joints. Make one continuous matte blue painted board with smooth coherent shading and restrained long grain. Preserve the curved board edges, brown ribs and gold rim at exact locations.'},
 'hull-water':{'rect':[1421,2957,2675,4211],'roi':[1570,3750,2510,4211],'feather':[128,100,128,0], 'note':'Repair the jagged vertical cyan/violet reflection boundaries near image x400 and x820 under the curved boat hull. Keep exactly the hull silhouette and waterline. Connect existing reflected colours gently along the real waterline; do not add a new reflection or change hull structure.'},
 'water-upper':{'rect':[2525,-115,3779,1139],'roi':[2690,-115,3620,1139],'feather':[140,0,140,230], 'note':'Only water appears here. Remove the artificial vertical strip boundaries at image x around 400 and 850, including where pink/lavender reflected brush planes are cut straight. Continue those existing broad soft water brush planes naturally through the middle. Do not add new bright reflections, floating objects, sparkles or decorations. Preserve the overall blue-lavender water and faint peach light already present.'},
 'water-lower':{'rect':[2525,909,3779,2163],'roi':[2690,909,3620,2050],'feather':[140,230,140,150], 'note':'Repair the artificial vertical strip edges at image x around 400 and 850 in the existing water reflections. Continue current broad soft pink/lavender reflected brush planes naturally across the middle. Preserve all actual rope and round-topped post contours exactly. No new objects, lights, reflections, ripples or sparkles. Use the preceding overlap only in its real indicated location.'},
}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):
 p=Path(p);assert p.resolve().is_relative_to(ROOT.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def frozen():
 assert sha(CORE)==CS and sha(EXT)==ES
 ext=Image.open(EXT).convert('RGB');assert ext.size==(4326,4326)
 assert ext.crop((115,115,4211,4211)).tobytes()==Image.open(CORE).convert('RGB').tobytes()
 return ext
def crop(im,r):return im.crop(tuple(v+115 for v in r))
def save(p,im,meta):
 p=Path(p);assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 write(str(p)+'.generation.json',{**ref(p),'createdAtUtc':now(),'pixels':list(im.size),'generatedByAI':False,'actualModel':None,'actualQuality':None,'sourceResampled':False,**meta})
 return ref(p)
def review():
 ext=frozen();q=BASE/'qa';names=[]
 for k in ['hull-upper','hull-lower','water-upper','water-lower']:
  names+=[k+'-'+z for z in ['full1254','return-left','return-right','return-top','return-bottom']]
 names += [f'y{y}-return-part{i:02d}' for y in [1024,2048,3072] for i in range(1,5)]
 names += [f'junction-x{x}-y{y}' for x in [1024,2048,3072] for y in [1024,2048,3072]]
 findings=[
  {'id':'hull-left','rect':[1780,2650,1890,3220],'note':'Irregular vertical paint edge crosses gold/brown rim and blue painted board.'},
  {'id':'hull-right','rect':[2200,2650,2290,3220],'note':'Second irregular vertical paint boundary on the same curved continuous board.'},
  {'id':'hull-waterline','rect':[1770,3890,2320,4096],'note':'Cyan versus violet lower water reflection is cut by jagged vertical insertion boundaries.'},
  {'id':'water-strip','rect':[2870,0,3420,1900],'note':'Faint peach/lavender water planes terminate at two repeated vertical pasted-strip edges.'},
  {'id':'left-interior','rect':[350,1750,880,3040],'note':'Wood and blue board lighting islands; finish agent handles the full precise breakdown.'},
  {'id':'left-lower-wood','rect':[955,3330,1220,3550],'note':'Brown hull board has a local orange paint island by the lower-right of y3072 part01.'},
 ]
 entries=[]
 for n in names:
  p=q/(n+'.png');m=read(str(p)+'.generation.json');r=m['actualTileAndHaloRectXYXY'];assert sha(p)==m['sha256']
  assert Image.open(p).convert('RGB').tobytes()==crop(ext,r).tobytes()
  hits=[e['id'] for e in findings if max(r[0],e['rect'][0])<min(r[2],e['rect'][2]) and max(r[1],e['rect'][1])<min(r[3],e['rect'][3])]
  entries.append({**ref(p),'rect':r,'actualView':True,'viewTool':'view_image','detail':'original','exactSourceCropVerified':True,'geometry':'no displaced contour found','status':'color-repair-required' if hits else 'pass-for-visible-scope','associatedFindings':hits})
 out={'createdAtUtc':now(),'reviewer':'root','candidate':ref(CORE),'extended':ref(EXT),'manifest':ref(BASE/'output/integration-manifest.json'),'actualViewedCount':len(entries),'entries':entries,'findings':findings,'formalAccepted':False,'all111Review':'Root41; independent west29 and vertical41 reports hold remaining actual observations.'}
 p=q/'review-root-hull-water-horizontal-41.json';assert not p.exists();write(p,out);return ref(p)
def prepare(k):
 t=TASKS[k];ext=frozen();p=B/'prompts'/(k+'.request.json');assert not p.exists()
 c=read(T/'source-contract-v2/source-contract.json');d=c['dayExtendedSnapshot']['snapshot'];assert sha(d['file'])==d['sha256']
 dimg=Image.open(d['file']).convert('RGB')
 refs=[]
 refs.append(save(B/'guides'/(k+'-current.png'),crop(ext,t['rect']),{'operation':'exact original-pixel current festival crop','derivedFrom':[ref(EXT)],'tileRectXYXY':t['rect']}))
 refs.append(save(B/'guides'/(k+'-day.png'),crop(dimg,t['rect']),{'operation':'exact original-pixel frozen DAY geometry crop','derivedFrom':[d],'tileRectXYXY':t['rect']}))
 refs.append(ref(STYLE));extra=''
 if k=='water-lower':
  pp=B/'native/water-upper.png';assert pp.exists();rr=TASKS['water-upper']['rect'];over=[t['rect'][0],t['rect'][1],t['rect'][2],rr[3]]
  local=[over[0]-rr[0],over[1]-rr[1],over[2]-rr[0],over[3]-rr[1]]
  refs.append(save(B/'guides/water-lower-previous-overlap.png',Image.open(pp).crop(local),{'derivedFrom':[ref(pp)],'sourceCropXYXY':local,'tileRectXYXY':over,'operation':'exact previous-native actual overlap, no pasted guide'}))
  extra=' Image4 is only the previous edit overlap at current local XYXY [0,0,1254,230]; match it there only, never elsewhere.'
 prompt=f'''Use case: precise local cleanup of an existing game map. Edit Image1, the actual final festival crop, in its exact 1254x1254 framing. Image2 is ONLY same-coordinate DAY geometry confirmation, never its lighting or palette. Image3 is the approved clean rounded high-finish Q game illustration style; no UI or objects from it. {extra}
 {t['note']}
 This is a subtle repair, not a redraw or restyle. Preserve every contour, object footprint, camera, scale, material identity, long grain, rope strand, board seam, gold trim and waterline. Keep the existing festival light, local hues, saturated but clean full cartoon rendering. The visible irregular vertical patch boundaries are artifacts to remove; create naturally continuous shading and brushwork on the same surface. Keep all four outer edges as close as possible to Image1, with no visible border; make corrections mainly around the specified interior defects. No duplication, relocation, added ornament, text, UI, watermark, pixel noise, texture blur, denoising or sharpening. Return one opaque original native 1254x1254 PNG. Configuration target gpt-image-2.5-sunburst/max, actual host model and quality are not exposed selectors.'''
 pp=B/'prompts'/(k+'.txt');pp.parent.mkdir(parents=True,exist_ok=True);pp.write_text(prompt,encoding='utf8')
 req={'prompt':prompt,'referenced_image_paths':[e['file'] for e in refs],'transparent_background':False};write(p,req)
 write(B/'prompts'/(k+'.prepared.json'),{'createdAtUtc':now(),'id':k,'task':t,'references':refs,'candidate':ref(CORE),'extended':ref(EXT),'prompt':ref(pp),'request':ref(p),'sourceContract':ref(T/'source-contract-v2/source-contract.json')})
 return {'request':str(p),'references':refs}
def record(k,raw):
 p=B/'native'/(k+'.png');assert not p.exists();r=Path(raw);im=Image.open(r);im.load();assert im.size==(1254,1254)
 if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
 pp=B/'prompts'/(k+'.prepared.json');m=read(pp);req=read(m['request']['file'])
 for e in m['references']+[m['prompt'],m['request']]:assert sha(e['file'])==e['sha256']
 p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r,p);assert sha(p)==sha(r)
 write(str(p)+'.generation.json',{**ref(p),'createdAtUtc':now(),'generatedByAI':True,'tool':'image_gen.imagegen','route':'builtin','configTarget':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool discloses no model or quality selectors or returned identity.','evidence':{'toolResultSourcePath':str(r),'toolResultSha256':sha(r)},'references':m['references'],'prepared':ref(pp),'pixels':[1254,1254],'resizedAfterGeneration':False,'finalArtUpscaled':False,'sourceBytesPreserved':True,'sourceRectXYXY':TASKS[k]['rect'],'formalAccepted':False,'visualQA':'pending composite and returns'})
 return ref(p)
def smooth(z):z=np.clip(z,0,1);return z*z*(3-2*z)
def build(keys,label):
 ext=frozen();a=np.array(ext);initial=a.copy();entries=[];union=np.zeros(a.shape[:2],bool)
 for k in keys:
  t=TASKS[k];native=B/'native'/(k+'.png');m=read(str(native)+'.generation.json');assert sha(native)==m['sha256']
  x,y,x1,y1=t['rect'];l,top,r,bot=t['roi'];fl,ft,fr,fb=t['feather'];xx=np.arange(x,x1)[None,:];yy=np.arange(y,y1)[:,None]
  # The lower edit fades into the upper source, not back into the faulty base.
  # Keep the first water source opaque through their real 230px overlap.
  overlap_override=k=='water-upper' and 'water-lower' in keys
  if overlap_override:fb=0
  w=np.ones((1254,1254),np.float32)
  for factor in [smooth((xx-l)/max(fl,1)),smooth((r-1-xx)/max(fr,1)),smooth((yy-top)/max(ft,1)) if ft else (yy>=top),smooth((bot-1-yy)/max(fb,1)) if fb else (yy<bot)]:w*=factor
  mask=(xx>=l)&(xx<r)&(yy>=top)&(yy<bot);w*=mask
  assert not np.any(w[:,np.arange(x,x1)<(350 if k=='left-water' else 1421)])
  region=a[y+115:y1+115,x+115:x1+115];src=np.array(Image.open(native).convert('RGB'));region[:]=np.rint(region*(1-w[:,:,None])+src*w[:,:,None]).astype(np.uint8)
  union[y+115:y1+115,x+115:x1+115]|=w>0
  mp=B/label/'masks'/(k+'.png');save(mp,Image.fromarray(np.rint(w*65535).astype(np.uint16)),{'operation':'explicit smoothstep compositing weight only, no texture blur','native':ref(native),'task':t})
  entries.append({'id':k,'native':ref(native),'record':ref(str(native)+'.generation.json'),'mask':ref(mp),'task':t,'actualFeather':[fl,ft,fr,fb],'upperSourceOpaqueThrough230pxLowerTransition':overlap_override})
 assert np.array_equal(a[~union],initial[~union])
 if 'left-water' not in keys:assert np.array_equal(a[:,:1536],initial[:,:1536])
 else:
  protected=np.ones(a.shape[:2],bool);protected[:,1536:]=False;protected[3710+115:,350+115:1421+115]=False
  assert np.array_equal(a[protected],initial[protected])
 out=B/label/'output';o=save(out/'extended-context.png',Image.fromarray(a),{'operation':'native local AI repair masked at exact coordinates','derivedFrom':[ref(EXT)]+[e['native'] for e in entries],'pixelScale':1,'formalAccepted':False})
 core=save(out/'r08_c16.png',Image.fromarray(a[115:4211,115:4211]),{'operation':'exact 4096 core crop','derivedFrom':[o],'pixelScale':1,'formalAccepted':False})
 qa=[]
 for k in keys:
  x,y,x1,y1=TASKS[k]['rect'];l,top,r,bot=TASKS[k]['roi']
  boxes={'full':[x,y,x1,y1],'return-left':[l-96,max(-115,top-96),l+96,min(4211,bot+96)],'return-right':[r-96,max(-115,top-96),r+96,min(4211,bot+96)],'return-top':[l-96,max(-115,top-96),r+96,min(4211,top+96)],'return-bottom':[l-96,max(-115,bot-96),r+96,min(4211,bot+96)]}
  for role,box in boxes.items():
   p=B/label/'qa'/(k+'-'+role+'.png');qa.append({**save(p,crop(Image.fromarray(a),box),{'operation':'exact original-pixel composite inspection crop','derivedFrom':[o],'tileRectXYXY':box,'actualView':False}), 'id':k,'role':role,'tileRectXYXY':box})
 manifest={'createdAtUtc':now(),'baseCandidate':ref(CORE),'baseExtended':ref(EXT),'candidate':core,'extended':o,'edits':entries,'allOutsideAlphaUnionPixelIdentical':True,'xLessThan1421PixelIdentical':'left-water' not in keys,'additionalLeftWaterDomain':[350,3710,1421,4211] if 'left-water' in keys else None,'noResamplingWarpOrTextureBlur':True,'QA':qa,'visualReview':'pending actual view','formalAccepted':False}
 p=B/label/'manifest.json';write(p,manifest);return ref(p)
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='review':r=review()
 elif cmd=='prepare':r=prepare(sys.argv[2])
 elif cmd=='record':r=record(sys.argv[2],sys.argv[3])
 elif cmd=='build':r=build(sys.argv[3:],sys.argv[2])
 else:raise SystemExit(cmd)
 print(json.dumps(r,ensure_ascii=False))
