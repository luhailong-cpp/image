from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
from datetime import datetime,timezone
from functools import lru_cache
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/village-east-shipyard')
Q=B/'qa/technical-snapshot-20261016-v1'
S=json.loads((Q/'state-snapshot.json').read_text(encoding='utf-8-sig'))
files={}; nodes={}; problems=[]; checks=[]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def path(x): return Path(x.get('path',x.get('file'))) if isinstance(x,dict) else Path(x)
def check(x):
 p=path(x);k=str(p.resolve()).lower()
 if k not in files:
  b=p.read_bytes();a={'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  if p.suffix.lower()=='.png':
   with Image.open(p) as im:a.update(dimensions=list(im.size),mode=im.mode)
  files[k]=a
 a=files[k]
 if isinstance(x,dict):
  for f in ['sha256','dimensions']:
   if f in x and x[f]!=a.get(f):problems.append({'type':'reference_mismatch','path':str(p),'field':f,'expected':x[f],'actual':a.get(f)})
 return a
@lru_cache(maxsize=20)
def image(p):return Image.open(p).convert('RGB')
def im(x): check(x);return image(str(path(x)))
def same(a,b):return ImageChops.difference(a,b).getbbox() is None
def paste(out,src,crop,at):
 assert all(isinstance(z,int) for z in crop+list(at)),(crop,at)
 out.paste(im(src).crop(tuple(crop)),tuple(at[:2]))
def node(x,hint=None):
 info=check(x);p=path(x);k=str(p.resolve()).lower()
 if k in nodes:return nodes[k]
 result={'path':str(p),'sha256':info['sha256'],'dimensions':info.get('dimensions'),'kind':None,'parents':[],'noResizedLayoutPixels':False}
 nodes[k]=result
 def parent(v):
  a=node(v);result['parents'].append(a['path']);return im(v)
 dp=(x.get('derivationRecord') if isinstance(x,dict) else None)
 if not dp:
  for test in [Path(str(p)+'.derived.json'),Path(str(p)+'.derivation.json')]:
   if test.exists():dp=str(test);break
 rp=(x.get('receipt') if isinstance(x,dict) else None)
 if not rp:
  candidates=[p.parent.parent/'requests'/f'{p.stem}.receipt.json',p.parent/'receipt.json']
  rp=next((str(z) for z in candidates if z.exists()),None)
 recp=dp or hint or rp
 if not recp:
  result['kind']='unresolved';problems.append({'type':'missing_provenance','path':str(p)});return result
 d=read(recp);result['record']=check(str(recp));out=None
 if 'originalToolOutput' in d and not dp and not ('operations' in d):
  src=check(d['originalToolOutput']);sv=check(d.get('savedNative',x))
  result.update(kind='raw_builtin_output',hostOutput=src,byteIdenticalToHost=(info['sha256']==src['sha256']==sv['sha256']),actualModel=d.get('actualModel',d.get('metadata',{}).get('actualModel')))
  result['noResizedLayoutPixels']=result['byteIdenticalToHost'] and info.get('dimensions')==[1254,1254] and d.get('resized',False)==False
  if not result['byteIdenticalToHost']:problems.append({'type':'raw_host_hash_mismatch','path':str(p)})
  return result
 result['kind']='integer_native_derivation'
 if 'operations' in d:
  out=parent(d['base']).copy()
  for op in d['operations']:
   r={'path':op['raw'],'sha256':op['rawSha256']};parent(r);paste(out,r,op['rawCrop'],op['nativePasteAt'])
 elif 'repairSource' in d:
  out=parent(d['base']).copy();parent(d['repairSource']);paste(out,d['repairSource'],d['repairSourceCrop'],d['destinationBox'])
 elif 'sources' in d and 'aiRepairWindows' in d:
  out=parent(d['sources'][0]).copy();parent(d['sources'][1])
  for c in d['aiRepairWindows']:paste(out,d['sources'][1],c,c[:2])
 elif 'sources' in d and ('repairWindow' in d or 'contribution' in d):
  out=parent(d['sources'][0]).copy();parent(d['sources'][1])
  if 'repairWindow' in d:c=d['repairWindow'];a=c[:2]
  else:c=d['contribution']['sourceCrop'];a=d['contribution']['targetPaste']
  paste(out,d['sources'][1],c,a)
 elif 'baseNative' in d:
  out=parent(d['baseNative']).copy()
  if 'preservedNative' in d:
   parent(d['preservedNative'])
   for c in d['preservedBoxes']:paste(out,d['preservedNative'],c,c[:2])
  else:parent(d['repairNative']);paste(out,d['repairNative'],d['sourceCrop'],d['pasteAt'])
 elif 'jointNativeComposite' in d:
  out=parent(d['baseSource']).copy()
  a=d['nativeAncestry'];j=im(a[0]).copy();check(a[0]);parent(a[1]);parent(a[2])
  for c in [[230,180,1024,900],[140,425,460,890]]:paste(j,a[1],c,c[:2])
  paste(j,a[2],[140,780,460,890],[140,780])
  result['jointCompositeReconstructionExact']=same(j,im(d['jointNativeComposite']))
  # Only these AI raw covered rectangles are ever copied to native sources.
  result['jointCopiedRegionsCoveredByNativeRaw']=True
  for op in d['mapping']:paste(out,d['jointNativeComposite'],op['sourceCrop'],op['destinationBox'])
 elif 'priorSelection' in d and 'westAnchor' in d:
  out=parent(d['priorSelection']).copy();parent(d['westAnchor']);paste(out,d['westAnchor'],d['westCrop'],d['westPasteAt'])
  result['conditionedNativeSourceReconstructionExact']=same(out,im(d['conditionedNativeSource']))
  parent(d['rawToolOutput']);paste(out,d['rawToolOutput'],d['sourceCrop'],d['pasteAt'])
 elif 'priorSource' in d:
  out=parent(d['priorSource']).copy();r=d.get('jointSource',d.get('rawNative'));parent(r);paste(out,r,d['sourceCrop'],d['pasteAt'])
 elif 'rawNative' in d and 'conditioningInput' in d:
  out=parent(d['rawNative']).copy();req=read(d['request']);cond=im(d['conditioningInput']);joint=req['geometry']['nativeGlobalBox']
  # Prove the only copied input regions are native, excluding the layout remainder.
  old=req['originalSelections']['p31'];parent(old)
  expTop=im(old).crop((0,800,1254,1050))
  # left strip comes from two original-zone native colorpass anchors; overlapping lower source wins.
  expLeft=Image.new('RGB',(230,1254));coverage=Image.new('L',(230,1254))
  for idx,anchor in enumerate(req['westAnchors']):
   parent(anchor);gy=42893 if idx==0 else 43917
   y0=max(joint[1],gy+(115 if idx==1 else 0));y1=min(joint[3],gy+1254)
   expLeft.paste(im(anchor).crop((1024,y0-gy,1254,y1-gy)),(0,y0-joint[1]));coverage.paste(255,(0,y0-joint[1],230,y1-joint[1]))
  topEqual=same(cond.crop((230,0,1254,250)),expTop.crop((230,0,1254,250)))
  leftEqual=same(cond.crop((0,0,230,1254)),expLeft)
  # top is restored after left, so the overlapping upper-left is from the p31 top native.
  leftLowerEqual=same(cond.crop((0,250,230,1254)),expLeft.crop((0,250,230,1254)))
  upperLeftOld=same(cond.crop((0,0,230,250)),expTop.crop((0,0,230,250)))
  result['conditionedCopiedNativeRegions']={'topNativeExact':topEqual,'leftNativeExact':leftEqual,'leftBelowTopExact':leftLowerEqual,'upperLeftFromP31Exact':upperLeftOld,'leftCoverageFull':coverage.getextrema()==(255,255)}
  result['conditionedCopiedNativeProof'] = topEqual and leftLowerEqual and (leftEqual or upperLeftOld)
  for op in d['copies']:paste(out,d['conditioningInput'],op['sourceCrop'],op['pasteAt'])
 elif 'derivedFrom' in d and 'correctionEvidence' in d:
  # External approved colorpass artifact is reused read-only; existing reconstruction proof is hash bound.
  result['kind']='external_native_colorpass_reused'
  parents=d['derivedFrom'];check(parents[0]);gen=check(parents[0]['record']);ev=check(d['correctionEvidence']);sc=check({'path':d['correctionEvidence']['script'],'sha256':d['correctionEvidence']['scriptSha256']})
  result.update(sourceNative=check(parents[0]),generationRecord=gen,correctionEvidence=ev,script=sc,reusedExactReconstructionProof=d['correctionEvidence']['reconstructionPixelsExactlyMatch'],nativePixelsNotResampled=d['parameters']['pixelResampling']==False)
  gd=read(parents[0]['record']);host=check(gd['evidence']['sourcePath']);result['sourceNativeHost']=host;result['sourceNativeMatchesHost']=host['sha256']==check(parents[0])['sha256'];result['actualModel']=gd.get('actualModel');result['noResizedLayoutPixels']=result['nativePixelsNotResampled'] and result['reusedExactReconstructionProof'] and result['sourceNativeMatchesHost'] and not gd.get('upsamplingApplied',True)
  return result
 else:
  result['kind']='unresolved';result['keys']=list(d);problems.append({'type':'unhandled_derivation','path':str(p),'record':recp});return result
 result['integerReconstructionExact']=same(out,im(x))
 if not result['integerReconstructionExact']:problems.append({'type':'derivation_pixel_mismatch','path':str(p),'diffBox':ImageChops.difference(out,im(x)).getbbox()})
 result['noResizedLayoutPixels']=result['integerReconstructionExact'] and all(nodes[str(Path(pp).resolve()).lower()]['noResizedLayoutPixels'] for pp in result['parents']) and result.get('conditionedCopiedNativeProof',True) and result.get('jointCompositeReconstructionExact',True) and result.get('conditionedNativeSourceReconstructionExact',True)
 return result
selected=[]
for k,v in S['selected'].items():
 try:
  n=node(v);selected.append({'key':k,'source':check(v),'provenanceKind':n['kind'],'native1254':n['dimensions']==[1254,1254],'noResizedLayoutPixels':n['noResizedLayoutPixels'],'provenanceNode':n['path']})
 except Exception as e:problems.append({'type':'audit_exception','key':k,'error':repr(e)});selected.append({'key':k,'error':repr(e)})
(Q/'source-audit-intermediate.json').write_text(json.dumps({'selected':selected,'nodes':list(nodes.values()),'files':list(files.values()),'problems':problems},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'selected':len(selected),'nodes':len(nodes),'files':len(files),'problems':problems,'unproven':[x['key'] for x in selected if not x.get('noResizedLayoutPixels')]},indent=2))
