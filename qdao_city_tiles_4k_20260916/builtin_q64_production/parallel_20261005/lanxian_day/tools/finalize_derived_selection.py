"""Select an entirely verified r09_c08 assembly, including derived native cells.

PREPARED ONLY: writing/importing this module does not select or clean anything.
CLI: python finalize_derived_selection.py r09_c08 [--check-only]

Prerequisites: 16 native cells; verified recursive source audit; exact assembly;
qa/root-final-review.json with sourceCore/sourceExtended, overview actuallyViewed,
reports (hashed JSON with checks/items), coverage, requiresRepair:false and an
actually reviewed northeast four-tile junction. Each final QA item must reference
an unchanged export and document an actual original-pixel view or exact-pixel
inheritance. The source pixels of every export are independently reconstructed.

Partial-core north context requires 89 scopes: standard53 + guide28 + north4 +
east4. Full north context requires93. Never label missing north halo as reviewed.
Actual builtin call counts are derived from source identities, never hardcoded.
This script deliberately has no cleanup, runtime publication or formal approval.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
from verify_native_sources import Audit,ROOT

def require(v,msg):
 if not v: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(p): return str(Path(p).resolve()).casefold()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):
 p=Path(p); return {'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def verify(p,h):
 require(isinstance(h,str) and len(h)==64,'Missing SHA256: '+str(p)); require(sha(p)==h,'SHA256 mismatch: '+str(p))
def pixels(p,size=None):
 with Image.open(p) as im:
  require(im.format=='PNG' and im.mode=='RGB','Expected RGB PNG: '+str(p))
  if size: require(im.size==tuple(size),'Wrong dimensions: '+str(p))
  return np.array(im)
def rgb(a): return hashlib.sha256(a.tobytes()).hexdigest()
def exact_crop(a,box):
 require(len(box)==4 and all(type(x) is int for x in box),'Integer source box required')
 x0,y0,x1,y1=box; require(0<=x0<x1<=a.shape[1] and 0<=y0<y1<=a.shape[0],'Source box outside image')
 return a[y0:y1,x0:x1]
def paste(dst,coverage,crop,xy):
 require(len(xy)==2 and all(type(x) is int for x in xy),'Integer destination required')
 x,y=xy; h,w=crop.shape[:2]
 require(x>=0 and y>=0 and x+w<=dst.shape[1] and y+h<=dst.shape[0],'Paste outside destination')
 dst[y:y+h,x:x+w]=crop; coverage[y:y+h,x:x+w]+=1
def write_new(p,value):
 require(not p.exists(),'Refusing existing output: '+str(p))
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def verify_assembly(tile,a,source_audit):
 expected={f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)}
 cells={c['cell']:c for c in source_audit['cells']}
 require(set(cells)==expected and all(c['verified'] for c in cells.values()),'All sixteen current source chains must verify')
 outputs={}
 for role,size in [('core',(4096,4096)),('extended',(4326,4326)),('preview',(1024,1024))]:
  item=a['outputs'][role]; path=Path(item['file']).resolve()
  require(path.parent==(tile/'candidate').resolve(),'Unexpected candidate output path'); verify(path,item['sha256']); outputs[role]=pixels(path,size)
 require(a['geometry']['coreInExtended']==[115,115,4211,4211],'Unexpected native halo geometry')
 require(np.array_equal(outputs['core'],outputs['extended'][115:4211,115:4211]),'Core not exact extended center crop')
 mappings={m['cell']:m for m in a['pixelMappings']}; sources=a['derivedFrom']
 require(len(mappings)==len(a['pixelMappings'])==len(sources)==16 and set(mappings)==expected,'Expected sixteen unique mapping entries')
 reconstructed={k:np.empty_like(outputs[k]) for k in ['core','extended']}
 coverage={k:np.zeros(outputs[k].shape[:2],dtype=np.uint8) for k in ['core','extended']}
 native=[]; hashes=set(); seen=set()
 for s in sources:
  cell=s['cell']; require(cell in expected and cell not in seen,'Duplicate/unexpected assembly source'); seen.add(cell)
  verify(s['file'],s['sha256']); verify(s['generationRecord'],s['generationRecordSha256'])
  require(norm(s['file'])==norm(tile/f'native/{cell}.png'),'Assembly uses non-current native source')
  require(norm(s['generationRecord'])==norm(cells[cell]['recordPath']) and s['generationRecordSha256']==cells[cell]['recordSha256'],'Assembly/source audit generation identity differs')
  require(s['sha256']==cells[cell]['imageSha256'],'Assembly/source audit pixels differ')
  require(s['sha256'] not in hashes,'Repeated native image bytes'); hashes.add(s['sha256'])
  image=pixels(s['file'],(1254,1254)); m=mappings[cell]
  for role,skey,dkey in [('core','coreSourceBox','coreDestinationXY'),('extended','sourceBox','extendedDestinationXY')]:
   paste(reconstructed[role],coverage[role],exact_crop(image,m[skey]),m[dkey])
  generation=load(s['generationRecord'])
  native.append({**s,'generation':generation,'verifiedSourceChain':cells[cell],'isDerived':generation.get('isDerived',False),'sourcePixelsCopiedExactly':True})
 for role in ['core','extended']:
  require(np.all(coverage[role]==1),role+' not covered exactly once'); require(np.array_equal(outputs[role],reconstructed[role]),role+' differs from native integer mapping')
 return outputs,native

def reconstruct_export(item,manifest,core):
 arr=pixels(item['file']); verify(item['file'],item['sha256'])
 if item.get('pixelMappings'):
  refs={norm(x['file']):x for x in item['derivedFrom']}
  reconstructed=np.empty_like(arr); coverage=np.zeros(arr.shape[:2],np.uint8)
  for mapping in item['pixelMappings']:
   source=refs.get(norm(mapping['source'])); require(source is not None,'Neighbor mapping lacks bound source identity')
   verify(source['file'],source['sha256']); im=pixels(source['file'],(4096,4096))
   paste(reconstructed,coverage,exact_crop(im,mapping['sourceBox']),mapping['destinationXY'])
  require(np.all(coverage==1) and np.array_equal(arr,reconstructed),'Neighbor export differs from integer source mappings')
 else:
  box=item.get('coreBox') or item.get('sourceBox'); require(box is not None,'QA crop lacks exact core source box')
  require(np.array_equal(arr,exact_crop(core,box)),'QA export differs from current core crop')
 return arr

def actual_or_inherited(item,arr):
 direct=any(item.get(k) is True for k in ['actuallyViewed','newlyActuallyViewed','actuallyViewedByThisReviewer'])
 if direct: return {'kind':'direct actual view','reportedByItem':True}
 inherited=item.get('inheritance') or item.get('inheritedEvidence')
 require(isinstance(inherited,dict),'No actual view or explicit inheritance evidence')
 # Explicit supported inheritance contract, no truthy statistics as substitutes.
 require(inherited.get('earlierActuallyViewed') is True and inherited.get('decodedRgbExactlyEqual') is True,'Inherited actual-view/identity proof incomplete')
 review=inherited.get('reviewFile'); reviewsha=inherited.get('reviewFileSha256')
 earlier=inherited.get('earlierCropFile'); earliersha=inherited.get('earlierCropSha256')
 require(review and earlier,'Inheritance needs hashed earlier review and crop paths')
 verify(review,reviewsha); verify(earlier,earliersha)
 require(np.array_equal(arr,pixels(earlier)),'Inherited crop bytes differ from final decoded pixels')
 previous=load(review); matching=[]
 for field in ['checks','items','views','scopes']:
  for old in previous.get(field,[]):
   oldpath=old.get('file') or old.get('path')
   if oldpath and norm(oldpath)==norm(earlier) and old.get('sha256')==earliersha: matching.append(old)
 require(matching,'Earlier crop identity absent from earlier review')
 require(any(any(m.get(k) is True for k in ['actuallyViewed','actualViewCompleted','newlyActuallyViewed','actuallyViewedByThisReviewer']) for m in matching),'Earlier review does not document actual view of that crop')
 return {'kind':'verified exact decoded-pixel inheritance','review':ref(review),'earlierCrop':ref(earlier)}

def verify_junction(record):
 require(record.get('kind')=='northeast_four_tile_junction' and record.get('actuallyViewed') is True and record.get('requiresRepair') is False,'Root northeast junction is not actually reviewed')
 for k in ['image','manifest']: verify(record[k]['file'],record[k]['sha256'])
 j=load(record['manifest']['file']); require(j['output']['sha256']==record['image']['sha256'],'Junction manifest output differs')
 a=pixels(record['image']['file'],(1024,1024)); out=np.empty_like(a); coverage=np.zeros(a.shape[:2],np.uint8)
 require(len(j['pixelMappings'])==4,'Four junction source mappings required')
 for m in j['pixelMappings']:
  verify(m['file'],m['sha256']); im=pixels(m['file'],(4096,4096)); crop=exact_crop(im,m['sourceBoxXYXY'])
  require(crop.shape==(512,512,3) and rgb(crop)==m['cropRawRGBSha256'],'Junction source crop differs')
  paste(out,coverage,crop,m['destinationXY'])
 require(np.all(coverage==1) and np.array_equal(a,out),'Junction board differs from actual source pixels')
 return record

def verify_qa(tile,a,context,arrays):
 rootpath=tile/'qa/root-final-review.json'; root=load(rootpath)
 require(root.get('tile')==tile.name and root.get('requiresRepair') is False,'Root final review not ready')
 for flag in ['formalAccepted','clientValidated','wholeCityComplete']: require(root.get(flag) is False,'Final review must preserve pending status: '+flag)
 for key,role in [('sourceCore','core'),('sourceExtended','extended')]:
  r=root[key]; verify(r['file'],r['sha256']); require(norm(r['file'])==norm(a['outputs'][role]['file']) and r['sha256']==a['outputs'][role]['sha256'],'Root reviewed different pixels')
 overview=root['overview']; require(overview.get('actuallyViewed') is True,'Root overview not viewed'); verify(overview['file'],overview['sha256'])
 require(overview['sha256']==a['outputs']['preview']['sha256'],'Root overview is not current candidate preview')
 partial=context.get('northContextKind')=='partial_core_band'; guide_count=28 if partial else 32
 exports={}; export_refs=[]
 for filename,count in [('qa.manifest.json',53),('guide-bands/manifest.json',guide_count),('external-north.manifest.json',4),('external-east.manifest.json',4)]:
  p=tile/'qa'/filename; manifest=load(p)
  require(manifest['source']['sha256']==a['outputs']['core']['sha256'],'QA manifest source differs: '+filename)
  require(len(manifest['checks'])==count,'QA manifest count differs: '+filename)
  if filename=='guide-bands/manifest.json':
   require(manifest.get('eastContext') is True and manifest.get('verticalGuideCoordinates')==[909,1933,2957,3981],'Wrong east guide-transition coverage')
   require(manifest.get('includesExternalNorthGuideBoundary') is (not partial),'Missing north halo falsely included or real halo excluded')
   expected_h={1139,2163,3187} if partial else {115,1139,2163,3187}
   require({x['coreCoordinate'] for x in manifest['checks'] if x['axis']=='y'}==expected_h,'Wrong horizontal guide coordinates')
  export_refs.append(ref(p))
  for item in manifest['checks']:
   k=norm(item['file']); require(k not in exports,'Duplicate exported QA scope')
   arr=reconstruct_export(item,manifest,arrays['core']); exports[k]={'item':item,'decodedRgbSha256':rgb(arr)}
 expected_total=53+guide_count+8; coverage=root['coverage']
 require(len(exports)==expected_total and coverage.get('exportedTotal')==expected_total and coverage.get('coveredScopes')==expected_total and coverage.get('allExportedScopesCoveredByActualViewsAndByteIdentity') is True,'Root coverage declaration incomplete')
 covered={}; reports=[]
 require(bool(root.get('reports')),'No hashed team review reports')
 for reportref in root['reports']:
  verify(reportref['file'],reportref['sha256']); report=load(reportref['file']); require(report.get('requiresRepair') is False,'Team review still needs repair')
  items=report.get('checks') if 'checks' in report else report.get('items'); require(isinstance(items,list) and items,'Unsupported/empty final QA report schema')
  reports.append(ref(reportref['file']))
  for item in items:
   k=norm(item['file']); require(k in exports and k not in covered,'Unexpected/duplicate reviewed QA scope')
   require(item.get('requiresRepair') is False and item['sha256']==exports[k]['item']['sha256'],'QA item requires repair or references older export')
   arr=pixels(item['file']); actualhash=rgb(arr)
   require(actualhash==exports[k]['decodedRgbSha256']==item.get('decodedRgbSha256',item.get('rawRGBSha256')),'Reviewed decoded pixels differ')
   evidence=actual_or_inherited(item,arr)
   covered[k]={'file':item['file'],'sha256':item['sha256'],'decodedRgbSha256':actualhash,'reviewReport':ref(reportref['file']),'viewEvidence':evidence}
 require(set(covered)==set(exports),'Final reviewed scope set does not match complete export set')
 additional=root.get('additionalRootChecks',[]); junctions=[x for x in additional if x.get('kind')=='northeast_four_tile_junction']
 require(len(junctions)==1,'One actual northeast four-tile junction review required')
 junction=verify_junction(junctions[0])
 return root,{'rootFinalReview':ref(rootpath),'teamReports':reports,'exportManifests':export_refs,'scopeCount':expected_total,'coveredScopes':list(covered.values()),'allScopesReconstructedFromCurrentPixels':True,'overview':overview,'northeastJunction':junction,'northContextKind':context.get('northContextKind','full_extended'),'actualNorthGuideBoundaryIncluded':not partial,'scopeLimit':'No claim of whole-city, runtime/client or unbuilt west/south neighbor acceptance.'}

def verify_context(tile):
 p=tile/'regional/context.json'; c=load(p)
 require(c['tile']==tile.name and c['pixelRectXYWH']==[28672,32768,4096,4096],'Wrong r09_c08 world extent')
 for name in ['northCore','eastCore','eastExtended']:
  r=c[name]; verify(r['file'],r['sha256']); pixels(r['file'],r['pixels'])
 if c.get('northContextKind')=='partial_core_band':
  require(not c.get('northExtended'),'Partial north must not invent an extended source')
  for name in ['northCoreBand','northKnownMask']:
   r=c[name]; verify(r['file'],r['sha256'])
  mask=c['northKnownMask']; require(mask['knownBoxXYXY']==[0,0,4326,115] and mask['unknownBoxXYXY']==[0,115,4326,230],'Incorrect north known/unknown extent')
 else:
  r=c['northExtended']; verify(r['file'],r['sha256']); pixels(r['file'],r['pixels'])
 return c

def selected_technical_artifacts(native):
 """Enumerate only technical assets explicitly linked by current derived cells.

 Prefer a cell's explicit technicalArtifacts list. Otherwise inspect technical
 mask/field/flow/alpha/weight links in its current processingEvidence and its
 current processing record only. Never glob historical repair directories.
 Additional upstream processing assets must be explicitly named in the current
 cell list; rejected version assets are not implicitly retained.
 """
 assets={}
 def add(path,h,role,cell):
  p=Path(path).resolve(); require(p.is_relative_to(ROOT),'Technical asset escapes production ROOT')
  require(p.suffix.lower() in ('.png','.npz','.npy','.py'),'Technical list expects selected mask/field or processing recipe: '+str(p))
  require(bool(role),'Technical asset role required'); verify(p,h)
  k=norm(p)
  if k in assets:
   require(assets[k]['sha256']==h,'Conflicting technical asset hashes')
   if cell not in assets[k]['requiredByCells']: assets[k]['requiredByCells'].append(cell)
  else: assets[k]={'file':str(p),'sha256':h,'role':role,'requiredByCells':[cell],'retention':'Required by currently adopted native processing only; preserve with selected output.'}
 def scan(obj,trail,cell):
  if isinstance(obj,list):
   for i,v in enumerate(obj): scan(v,trail+[str(i)],cell)
  elif isinstance(obj,dict):
   for k,v in obj.items():
    label='/'.join(trail+[k]); technical=any(x in label.lower() for x in ('mask','field','flow','alpha','weight'))
    if technical and isinstance(v,str) and Path(v).suffix.lower() in ('.png','.npz','.npy'):
     h=obj.get(k+'Sha256')
     if k in ('path','file'): h=obj.get('sha256',h)
     if k.endswith('Path'): h=obj.get(k[:-4]+'Sha256',h)
     require(h is not None,'Current technical asset lacks explicit hash: '+label)
     add(v,h,label,cell)
    elif isinstance(v,(dict,list)): scan(v,trail+[k],cell)
 for source in native:
  if not source['isDerived']: continue
  cell=source['cell']; g=source['generation']; explicit=g.get('technicalArtifacts')
  prior=set(assets)
  if explicit is not None:
   require(isinstance(explicit,list) and explicit,'Explicit technicalArtifacts must be nonempty')
   for item in explicit: add(item.get('file') or item.get('path'),item['sha256'],item['role'],cell)
  else:
   evidence=g['processingEvidence']; scan(evidence,['processingEvidence'],cell)
   process=evidence['processing']; path=process.get('file') or process.get('path'); verify(path,process['sha256'])
   scan(load(path),['currentProcessing'],cell)
  require(any(cell in x['requiredByCells'] for x in assets.values()),'No explicitly linked technical mask/field assets for derived cell '+cell)
 return sorted(assets.values(),key=lambda x:x['file'])

def execute(tile,check_only=False):
 require(tile==ROOT/'r09_c08','This preparatory finalizer is specific to r09_c08')
 out=tile/'selected'; names=['core4096.png','extended4326.png','preview1024.png','delivery.manifest.json','selection-proof.json','native-call-audit.json','native-source-audit.json','provenance-records.json']
 require(all(not (out/n).exists() for n in names),'Selected output already exists; never overwrite')
 source_audit=Audit(tile).run(require_complete=True)
 require(source_audit['selectionSourceReady'],'Recursive native source verification failed or native grid incomplete: '+json.dumps(source_audit['issues'],ensure_ascii=False))
 assembly_path=tile/'candidate/assembly.manifest.json'; a=load(assembly_path); arrays,native=verify_assembly(tile,a,source_audit)
 context=verify_context(tile); root_review,qa=verify_qa(tile,a,context,arrays)
 technical=selected_technical_artifacts(native)
 now=datetime.now(timezone.utc).isoformat(); derived=[x for x in native if x['isDerived']]
 direct_hashes={x['sha256'] for x in native if not x['isDerived']}
 nativecalls=[x for x in source_audit['calls'] if 'native' in x['categories']]; regionalcalls=[x for x in source_audit['calls'] if 'regional' in x['categories']]
 require(not ({x['sourceOutputSha256'] for x in nativecalls}&{x['sourceOutputSha256'] for x in regionalcalls}),'Native/regional output call identities overlap')
 callaudit={'createdAtUtc':now,'nativeBuiltinCallsWithDistinctRecordedOutput':len(nativecalls),'regionalBuiltinCallsSeparately':len(regionalcalls),'selectedCells':16,'directBuiltinNativeCells':16-len(derived),'locallyDerivedNativeCells':len(derived),'derivedCellNames':[x['cell'] for x in derived],'localProcessingAddsBuiltinCalls':0,'directBuiltinOutputHashes':sorted(direct_hashes),'nativeCalls':nativecalls,'regionalCalls':regionalcalls,'explicitRejectedNativeCallCount':sum(any(isinstance(s,str) and s.startswith('rejected') for s in x['recordStatuses']) for x in nativecalls),'countMethod':source_audit['countMeaning'],'statusPolicy':'Historical pending/rejected statuses are preserved. Non-direct output is not automatically classified as rejected; some are edit ancestors or native repair inputs.'}
 snapshots=[]
 for record in source_audit['records']:
  verify(record['recordPath'],record['recordSha256']); snapshots.append({'record':ref(record['recordPath']),'contents':load(record['recordPath'])})
 proof={'createdAtUtc':now,'sourceAssembly':ref(assembly_path),'coreExactlyCenterCrop':True,'all16CurrentCellCoreMappingsExactlyCopied':True,'all16CurrentCellExtendedMappingsExactlyCopied':True,'everyProductionPixelCoveredExactlyOnce':True,'currentNativeDimensions':[1254,1254],'locallyDerivedCellCount':len(derived),'derivedProcessingEvidencePreserved':True,'assemblyResampling':'none','sourceCellsMayContainRecordedNativeAIRepairAndBoundedLocalProcessing':bool(derived),'postAssemblyProcessing':False,'selectedCopyByteIdenticalToCandidate':True,'recursiveSourceEvidenceVerified':True,'rootAndTeamActualViewEvidenceVerified':True,'completeQAScopeCount':qa['scopeCount'],'coreLeft230RawRGBSha256':rgb(arrays['core'][:,:230]),'extendedLeft230RawRGBSha256':rgb(arrays['extended'][:,:230])}
 summary={'tile':tile.name,'verifiedNativeCells':16,'derivedCells':len(derived),'nativeBuiltinCalls':len(nativecalls),'regionalBuiltinCalls':len(regionalcalls),'qaScopes':qa['scopeCount'],'checkOnly':check_only,'cleanupPerformed':False}
 if check_only: return summary
 # Last identity check immediately before any selected output is written.
 for s in a['derivedFrom']: verify(s['file'],s['sha256']); verify(s['generationRecord'],s['generationRecordSha256'])
 for value in a['outputs'].values(): verify(value['file'],value['sha256'])
 require(all(not (out/n).exists() for n in names),'Selected file appeared during verification')
 out.mkdir(exist_ok=True); outputs={}
 for role,name in [('core','core4096.png'),('extended','extended4326.png'),('preview','preview1024.png')]:
  src=a['outputs'][role]; dest=out/name; shutil.copyfile(src['file'],dest); verify(dest,src['sha256'])
  outputs[role]={**ref(dest),'pixels':list(Image.open(dest).size),'productionPixels':role!='preview'}
 write_new(out/'native-source-audit.json',source_audit); write_new(out/'native-call-audit.json',callaudit); write_new(out/'selection-proof.json',proof)
 write_new(out/'provenance-records.json',{'createdAtUtc':now,'generationRecordSnapshots':snapshots,'note':'Exact text record snapshots and hashes; binary source retention/cleanup is a separate operation. Historical records are not rewritten.'})
 manifest={'schemaVersion':2,'createdAtUtc':now,'tile':tile.name,'status':'qualified_complete_4k_candidate_pending_remaining_adjacent_edges_and_formal_acceptance','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'runtimePublished':False,'outputs':outputs,'geometry':a['geometry'],'pixelRectXYWH':context['pixelRectXYWH'],'worldRect':context['worldRect'],'selectionProof':ref(out/'selection-proof.json'),'technicalArtifacts':technical,'sourceChain':{'assembly':ref(assembly_path),'nativeSources':native,'recursiveSourceAudit':ref(out/'native-source-audit.json'),'nativeCallAudit':ref(out/'native-call-audit.json'),'fullGenerationRecordSnapshots':ref(out/'provenance-records.json'),'regionalContext':ref(tile/'regional/context.json'),'regionalReview':ref(tile/'regional/visual-review.json'),'actualRegionalCallCount':len(regionalcalls),'locallyDerivedNativeCells':[{'cell':x['cell'],'generationRecord':ref(x['generationRecord']),'processingEvidence':x['generation'].get('processingEvidence')} for x in derived]},'nativeCounts':{'selectedCells':16,'directBuiltinCells':16-len(derived),'derivedCells':len(derived),'actualNativeBuiltinCalls':len(nativecalls),'regionalCallsSeparately':len(regionalcalls)},'processingDeclaration':{'configuredTargets':[{'cell':x['cell'],'model':x['generation']['configSnapshot']['model'],'quality':x['generation']['configSnapshot']['quality']} for x in native],'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'actualIdentityExplanation':'Underlying builtin selectors and returned model/quality are undisclosed. Local derivations do not invoke a model. Config snapshots are targets only.','sourceCellProcessing':'See each derived cell local_native_processing chain for native AI repair, geometry / RGB fields, masks, limits and actual reviews. Do not infer globally unprocessed cells from integer assembly.','assembly':'Integer crop/paste of current native cell pixels; no additional resampling, tone, flow or patch after assembly.','productionScaling':False,'previewOnlyDownsample':True,'selection':'Byte-identical candidate copy'},'qaSummary':qa,'minorObservations':root_review.get('minorObservations',[]),'futureEastReferenceForR09C07':{'core':outputs['core'],'extended':outputs['extended'],'useSelectedOnly':True,'coreLeft230RawRGBSha256':proof['coreLeft230RawRGBSha256'],'extendedLeft230RawRGBSha256':proof['extendedLeft230RawRGBSha256'],'westNeighborSeamNotYetValidated':True},'remaining':['Unbuilt west/south neighboring joins and their junctions.','Formal art acceptance, client loading/navigation, runtime publication and whole-city completion.'],'retention':{'state':'selected_verified_cleanup_pending','cleanupPerformedByThisScript':False,'technicalArtifacts':technical,'technicalSelectionPolicy':'Only explicit technical assets linked by currently adopted local processing; never blanket-retain historical masks.','policy':'Keep selected game assets, current active references, required technical assets and all textual provenance. Cleanup must independently resolve current consumers and exact target paths.'}}
 write_new(out/'delivery.manifest.json',manifest)
 return {**summary,'outputs':outputs,'deliveryManifest':ref(out/'delivery.manifest.json')}

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('tile'); p.add_argument('--check-only',action='store_true'); args=p.parse_args()
 tile=Path(args.tile)
 if not tile.is_absolute(): tile=ROOT/tile
 tile=tile.resolve(strict=True); require(tile.is_relative_to(ROOT) and tile.parent==ROOT,'Tile escapes production ROOT')
 print(json.dumps(execute(tile,args.check_only),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
