"""Read-only provenance audit for native cells and explicitly linked local processing.

Usage: python verify_native_sources.py r09_c08 [--output path] [--require-complete]
Only --output writes a new audit JSON within this production ROOT. Existing output
is never overwritten. Missing fields, files and mismatched hashes are reported;
they never become an implicit pass. No image generation or acceptance occurs.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
HEX=re.compile(r'^[0-9a-fA-F]{64}$')
CELL=re.compile(r'^r0[1-4]_c0[1-4]$')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p): return str(Path(p).resolve()).casefold()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pathlike(v): return isinstance(v,str) and (bool(re.match(r'^[A-Za-z]:[\\/]',v)) or v.startswith('/'))

class Audit:
 def __init__(self,tile):
  self.tile=tile; self.issues=[]; self.records={}; self.calls={}; self.checked={}; self.in_progress=set(); self.link_hashes={}; self.links=[]; self.observed_metadata={}
 def issue(self,owner,code,message):
  item={'owner':str(owner),'code':code,'message':message,'verified':False}
  if item not in self.issues: self.issues.append(item)
 def check(self,p,expected,owner,label='file'):
  if not pathlike(str(p)):
   self.issue(owner,'non_absolute_reference',f'{label}: {p}'); return False
  p=Path(p); k=key(p)
  if not isinstance(expected,str) or not HEX.fullmatch(expected):
   self.issue(owner,'missing_or_invalid_sha256',f'{label}: {p}'); return False
  if not p.is_file(): self.issue(owner,'missing_file',f'{label}: {p}'); return False
  try:
   actual=self.checked.setdefault(k,digest(p))
  except Exception as exc:
   self.issue(owner,'file_read_error',f'{label}: {p}: {type(exc).__name__}: {exc}'); return False
  if actual.lower()!=expected.lower():
   self.issue(owner,'hash_mismatch',f'{label}: {p}; expected {expected}; actual {actual}'); return False
  self.link_hashes.setdefault(k,set()).add(expected.lower()); return True
 def load(self,p,owner):
  try: return read(p)
  except Exception as exc:
   self.issue(owner,'json_read_error',f'{p}: {type(exc).__name__}: {exc}'); return None
 def pairs(self,obj):
  if isinstance(obj,list):
   for v in obj: yield from self.pairs(v)
  elif isinstance(obj,dict):
   for k,v in obj.items():
    if pathlike(v) and k not in ('reviewer','agent','owner','worker'):
     candidates=[k+'Sha256']
     if k in ('path','file'): candidates=['sha256']+candidates
     if k=='qaFile': candidates.append('sha256')
     if k.endswith('Path'): candidates.insert(0,k[:-4]+'Sha256')
     if k.endswith('File'): candidates.insert(0,k[:-4]+'Sha256')
     if k=='receipt': candidates.insert(0,'receiptSha256')
     sha=next((obj[h] for h in candidates if h in obj),None)
     yield k,v,sha
    if isinstance(v,(list,dict)): yield from self.pairs(v)
 def register_hashes(self,obj):
  for _,p,h in self.pairs(obj):
   if isinstance(h,str) and HEX.fullmatch(h): self.link_hashes.setdefault(key(p),set()).add(h.lower())
 def inspect_links(self,obj,owner,skip=()):
  self.register_hashes(obj)
  for name,p,h in self.pairs(obj):
   if name in skip: continue
   if h is None:
    known=self.link_hashes.get(key(p),set())
    if len(known)==1: h=next(iter(known))
    elif key(p) in self.observed_metadata: continue
    else:
     self.issue(owner,'unhashed_reference',f'{name}: {p}'); continue
   self.check(p,h,owner,name)
 def require_null(self,r,owner):
  for k in ('actualModel','actualQuality'):
   if k not in r or r[k] is not None: self.issue(owner,'actual_model_quality_not_null',k)
  submitted=r.get('submittedParameters')
  if not isinstance(submitted,dict): self.issue(owner,'missing_submitted_parameters','submittedParameters must be an object'); return {}
  for k in ('model','quality'):
   if k not in submitted or submitted[k] is not None: self.issue(owner,'submitted_selector_not_null',k)
  if not r.get('unverifiedReason'): self.issue(owner,'missing_unverified_reason','Host-managed model/quality must be explicitly unconfirmed.')
  return submitted
 def image(self,r,owner,override=None):
  declared=r.get('file'); expected=r.get('sha256'); resolved=Path(override or declared or '')
  relocation=None
  # Archived unchanged generation records can retain the pre-adoption declared path.
  # Only an exact same-name sibling with the already recorded hash is a valid relocation.
  sibling=Path(str(owner).removesuffix('.generation.json'))
  if override is None and sibling.is_file() and sibling!=resolved and isinstance(expected,str):
   if digest(sibling)==expected:
    relocation={'declaredPath':declared,'verifiedArchivedImagePath':str(sibling),'sha256':expected}; resolved=sibling
  ok=self.check(resolved,expected,owner,'record image')
  if ok:
   try:
    with Image.open(resolved) as im:
     size=list(im.size); fmt=im.format
    declaredsize=r.get('pixels') or [r.get('width'),r.get('height')]
    if size!=[1254,1254] or size!=declaredsize or fmt!='PNG':
     self.issue(owner,'native_dimensions_or_format_mismatch',f'actual {size} {fmt}; declared {declaredsize}')
   except Exception as exc: self.issue(owner,'image_read_error',f'{resolved}: {type(exc).__name__}: {exc}')
  return str(resolved),relocation
 def record(self,p,override=None):
  p=Path(p); k=key(p)
  if k in self.records: return self.records[k]
  if k in self.in_progress:
   self.issue(p,'cyclic_generation_reference','Recursive provenance cycle'); return None
  self.in_progress.add(k); start=len(self.issues); r=self.load(p,p)
  if not isinstance(r,dict):
   self.in_progress.remove(k); return None
  self.register_hashes(r)
  imagepath,relocation=self.image(r,p,override)
  submitted=self.require_null(r,p)
  for n in ('model','quality','builtin_product','verified_on','sources'):
   if n not in r.get('configSnapshot',{}): self.issue(p,'missing_config_snapshot_field',n)
  when=r.get('generatedAt') or r.get('createdAt')
  try:
   if datetime.fromisoformat(when.replace('Z','+00:00')).utcoffset() is None: raise ValueError('timezone missing')
  except Exception as exc: self.issue(p,'invalid_timestamp',str(exc))
  entry={'recordPath':str(p),'recordSha256':digest(p),'imagePath':imagepath,'imageSha256':r.get('sha256'),'tool':r.get('tool'),'isDerived':r.get('isDerived',False),'statusInRecord':r.get('status'),'children':[],'archivedImageRelocation':relocation}
  if r.get('tool')=='image_gen.imagegen' and r.get('route')=='builtin' and not r.get('isDerived'):
   self.builtin(r,p,entry,submitted)
  elif r.get('tool')=='local_native_processing' and r.get('isDerived') is True:
   self.derived(r,p,entry,submitted)
  else:
   self.issue(p,'unsupported_generation_schema',f"tool={r.get('tool')!r}, route={r.get('route')!r}, isDerived={r.get('isDerived')!r}; no assumed pass")
  entry['ownIssueCodes']=[i['code'] for i in self.issues[start:] if i['owner']==str(p)]
  entry['verified']=not entry['ownIssueCodes'] and all(self.records.get(key(c),{}).get('verified',False) for c in entry['children'])
  self.records[k]=entry; self.in_progress.remove(k); return entry
 def builtin(self,r,p,entry,submitted):
  e=r.get('evidence',{}); output=e.get('sourceOutputPath'); outhash=e.get('sourceOutputSha256')
  sourceok=self.check(output or '',outhash,p,'actual builtin source output')
  if outhash!=r.get('sha256'): self.issue(p,'source_image_identity_mismatch','Native record and builtin source output hashes differ')
  if isinstance(outhash,str):
   category='regional' if r.get('guideOnly') or 'regional' in p.name or ('regional' in p.parts and not r.get('cell')) else 'native'
   c=self.calls.setdefault(outhash,{'sourceOutputSha256':outhash,'sourceOutputPaths':[],'generationRecords':[],'categories':[],'sourcePixelsVerified':False,'recordStatuses':[]})
   for arr,v in [(c['sourceOutputPaths'],output),(c['generationRecords'],str(p)),(c['categories'],category),(c['recordStatuses'],r.get('status'))]:
    if v not in arr: arr.append(v)
   c['sourcePixelsVerified']|=sourceok
  receipt=e.get('toolResultPath') or e.get('receipt') or e.get('actualReceipt'); rh=e.get('toolResultSha256') or e.get('receiptSha256') or e.get('actualReceiptSha256')
  receiptok=self.check(receipt or '',rh,p,'actual builtin receipt'); q=self.load(receipt,p) if receiptok else None
  prompt=submitted.get('prompt')
  if not isinstance(prompt,str) or not prompt.strip(): self.issue(p,'missing_actual_prompt','submittedParameters.prompt')
  promptvalue=r.get('promptFile') or r.get('prompt')
  if pathlike(promptvalue):
   if self.check(promptvalue,r.get('promptSha256'),p,'actual prompt file'):
    if Path(promptvalue).read_text(encoding='utf-8-sig')!=prompt: self.issue(p,'prompt_text_mismatch','Prompt file versus actual submitted prompt')
  elif promptvalue!=prompt: self.issue(p,'prompt_text_mismatch','Inline prompt versus actual submitted prompt')
  refs=r.get('references')
  if not isinstance(refs,list) or not refs:
   self.issue(p,'missing_reference_evidence','Expected actual reference paths, roles and hashes'); refs=[]
  for ref in refs:
   if not ref.get('role'): self.issue(p,'missing_reference_role',str(ref.get('path')))
   self.check(ref.get('path',''),ref.get('sha256'),p,'actual attached reference')
  if [key(v) for v in submitted.get('referenced_image_paths',[])]!=[key(v['path']) for v in refs]: self.issue(p,'submitted_reference_list_mismatch','Ordered attachment list differs from reference records')
  if q:
   if q.get('prompt')!=prompt: self.issue(p,'receipt_prompt_mismatch','Receipt and submission prompt differ')
   if key(q.get('sourceOutputPath',''))!=key(output or ''): self.issue(p,'receipt_source_mismatch','Receipt actual output path differs')
   if [key(x['path']) for x in q.get('references',[])]!=[key(x['path']) for x in refs]: self.issue(p,'receipt_references_mismatch','Receipt reference ordering differs')
   if [x.get('role') for x in q.get('references',[])]!=[x.get('role') for x in refs]: self.issue(p,'receipt_reference_roles_mismatch','Receipt and generation reference roles differ')
   try:
    rt=datetime.fromisoformat(r['generatedAt'].replace('Z','+00:00')); qt=datetime.fromisoformat(q['generatedAt'].replace('Z','+00:00'))
    if rt!=qt: self.issue(p,'receipt_timestamp_mismatch','Receipt and generation output timestamps differ')
   except Exception as exc: self.issue(p,'receipt_timestamp_invalid',str(exc))
   self.compare_submission(q,p,prompt,refs,'receipt')
  request=e.get('actualRequest')
  if request and self.check(request,e.get('actualRequestSha256'),p,'actual request'):
   req=self.load(request,p)
   if isinstance(req,dict):
    self.compare_submission(req,p,prompt,refs,'actual request')
    entry['actualRequestEvidence']={'path':request,'sha256':e['actualRequestSha256'],'historicallyHashBound':True}
  job=r.get('sourceJob'); jh=r.get('sourceJobSha256')
  if not job:
   entry['recordingPathNoJob']=True
   entry['submissionEvidence']={'kind':'actual receipt plus generation record','receiptPath':receipt,'receiptSha256':rh,'note':'No sourceJob emitted by this recording path. Actual submitted prompt, ordered references with roles and hashes, timestamp, source output and null host-managed model/quality are verified from the receipt and generation record. Optional nearby request files are not inferred.'}
  elif self.check(job,jh,p,'actual source job'):
   j=self.load(job,p)
   if j:
    self.compare_submission(j,p,prompt,refs,'source job')
    if j.get('prompt')!=prompt: self.issue(p,'job_prompt_mismatch','Source job prompt differs')
    if r.get('sourceJobKind')=='actual-request':
     if [key(x['path']) for x in j.get('references',[])]!=[key(x['path']) for x in refs]: self.issue(p,'job_references_mismatch','Explicit actual-request attachment list differs')
    else:
     if key(j.get('sourceOutputPath',''))!=key(output or ''): self.issue(p,'job_output_mismatch','Source job output differs')
     if j.get('expectedSha256')!=outhash: self.issue(p,'job_expected_output_mismatch','Source job expectedSha256 differs')
    self.archive_dependencies(j,p,entry)
  entry['sourceOutputSha256']=outhash
 def compare_submission(self,j,p,prompt,refs,label):
  if j.get('prompt')!=prompt: self.issue(p,'submission_prompt_mismatch',label)
  actual=j.get('references',[])
  if [(key(x.get('path','')),x.get('role')) for x in actual]!=[(key(x.get('path','')),x.get('role')) for x in refs]: self.issue(p,'submission_references_mismatch',label)
  for x,y in zip(actual,refs):
   if 'sha256' in x and x['sha256']!=y.get('sha256'): self.issue(p,'submission_reference_hash_mismatch',label+': '+str(x.get('path')))
  selectors=j.get('submittedParameters',{})
  for name in ('model','quality'):
   if name in selectors and selectors[name] is not None: self.issue(p,'submitted_selector_not_null',label+': '+name)
   actual_name='actual'+name.capitalize()
   if actual_name in j and j[actual_name] is not None: self.issue(p,'actual_model_quality_not_null',label+': '+actual_name)
  if 'prompt' in selectors and selectors['prompt']!=prompt: self.issue(p,'submission_prompt_mismatch',label+' selectors')
  if 'referenced_image_paths' in selectors and [key(x) for x in selectors['referenced_image_paths']]!=[key(x['path']) for x in refs]: self.issue(p,'submission_references_mismatch',label+' selectors')
 def archive_dependencies(self,j,p,entry):
  for constraint in j.get('constraints',[]):
   binding=constraint.get('archiveBinding')
   if not isinstance(binding,dict): continue
   start=len(self.issues); contract=binding.get('contract',{}); cp=contract.get('file','')
   if not self.check(cp,contract.get('sha256'),p,'archived dependency contract'): continue
   c=self.load(cp,p)
   if not isinstance(c,dict): continue
   sp=constraint.get('file',''); sh=constraint.get('sha256')
   if key(c.get('baseNative',''))!=key(sp) or c.get('baseSha256')!=sh: self.issue(p,'archive_source_identity_mismatch',cp)
   if not self.check(sp,sh,p,'archived dependency image'): continue
   gen=c.get('generationRecord','')
   if self.check(gen,c.get('generationRecordSha256'),p,'archived dependency generation'):
    entry['children'].append(gen); self.record(gen,sp)
   # originalFile is an historical identity, not a requirement that a mutable
   # current native path retain rejected pixels after an approved adoption.
   for copy in c.get('archiveCopies',[]): self.check(copy.get('archiveFile',''),copy.get('sha256'),p,'exact archived historical copy')
   try:
    with Image.open(sp) as im: archived=im.convert('RGB')
    box=c['southDependencyBoxXYXY']; raw=hashlib.sha256(archived.crop(box).tobytes()).hexdigest()
    if box!=constraint.get('sourceBox') or box!=binding.get('sourceBox') or raw!=c.get('southRawRGBSha256') or raw!=binding.get('bottom230DecodedRgbSha256'): self.issue(p,'archive_dependency_crop_mismatch',cp)
    gd=j.get('guideDerivation',{}); guide=gd.get('guide',''); strict_guide_verified=False
    if self.check(guide,gd.get('guideSha256'),p,'archive-dependent actual guide'):
     with Image.open(guide) as im: guide_rgb=im.convert('RGB')
     target=constraint['guaranteedExactFirst115TargetBox']; sx,sy=box[:2]; w=target[2]-target[0]; h=target[3]-target[1]
     if constraint.get('side')!='north' or target!=[0,0,1254,115]: self.issue(p,'unsupported_archive_strict_strip',str(target))
     elif guide_rgb.crop(target).tobytes()!=archived.crop((sx,sy,sx+w,sy+h)).tobytes(): self.issue(p,'archive_strict_guide_pixels_mismatch',guide)
     else: strict_guide_verified=True
    original=binding.get('previousPreparationSource',{})
    if original.get('sha256')!=sh: self.issue(p,'archive_original_identity_mismatch',cp)
    current=original.get('file',''); rows=c['unchangedRowsHalfOpen']
    with Image.open(current) as im: current_rgb=im.convert('RGB')
    fixedbox=[0,rows[0],archived.width,rows[1]]
    if current_rgb.size!=archived.size or current_rgb.crop(fixedbox).tobytes()!=archived.crop(fixedbox).tobytes(): self.issue(p,'archive_current_immutable_rows_changed',current)
    observation={'contract':contract,'archivedSource':{'file':sp,'sha256':sh},'sourceBoxXYXY':box,'decodedRgbSha256':raw,'currentNativeObservedSha256':digest(Path(current)),'currentNativeUnchangedRows':rows,'guideStrictTop115Reconstructed':strict_guide_verified,'historicalOriginalPathRequiredToRetainWholeFileHash':False}
    qa=self.tile/'ready-cell-qa'/j['cell']/'actual-pixel-review.json'
    if qa.exists(): observation['readyCellQaEvidence']=self.archive_qa(qa,p,sp,contract)
    else: observation['readyCellQaEvidence']={'status':'not yet recorded; no visual claim inferred'}
    observation['verified']=len(self.issues)==start
    entry.setdefault('archivedDependencyProofs',[]).append(observation)
   except Exception as exc: self.issue(p,'archive_dependency_verification_error',f'{type(exc).__name__}: {exc}')
 def archive_qa(self,qa,p,archive,contract):
  start=len(self.issues); review=self.load(qa,p)
  if not isinstance(review,dict): return {'verified':False}
  manifest=review.get('sourceManifest',{}); mp=manifest.get('file','')
  m=self.load(mp,p) if self.check(mp,manifest.get('sha256'),p,'actual QA source manifest') else None
  if not isinstance(m,dict): return {'verified':False}
  checks=review.get('checks',[]); declared={key(v['file']):v for v in m.get('checks',[])}; archive_mappings=0
  reviewed_paths=[key(v.get('file','')) for v in checks]
  if not checks or len(declared)!=len(m.get('checks',[])) or len(set(reviewed_paths))!=len(reviewed_paths) or set(reviewed_paths)!=set(declared): self.issue(p,'qa_review_scope_coverage_mismatch',str(qa))
  if review.get('actualViewCount')!=len(checks): self.issue(p,'qa_review_view_count_mismatch',str(qa))
  for check in checks:
   f=check.get('file',''); sourcecheck=declared.get(key(f),{})
   for name in ('sha256','width','height','decodedRgbSha256','pixelMappings'):
    if check.get(name)!=sourcecheck.get(name): self.issue(p,'qa_review_manifest_mismatch',f+': '+name)
   if not self.check(f,check.get('sha256'),p,'actually reviewed QA pixels'): continue
   with Image.open(f) as im: pixels=im.convert('RGB')
   canvas=Image.new('RGB',(check['width'],check['height'])); covered=Image.new('1',canvas.size)
   for mapping in check.get('pixelMappings',[]):
    src=mapping['source']; sf=src['file']
    if not self.check(sf,src.get('sha256'),p,'QA source pixels'): continue
    generation=src.get('generationRecord',{})
    self.check(generation.get('file',''),generation.get('sha256'),p,'QA source generation')
    with Image.open(sf) as im:
     box=mapping['sourceBoxXYXY']
     if len(box)!=4 or not all(type(x) is int for x in box) or not (0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height): raise ValueError('Invalid integer QA source crop: '+f)
     crop=im.convert('RGB').crop(box)
    if hashlib.sha256(crop.tobytes()).hexdigest()!=mapping.get('decodedRgbSha256'): self.issue(p,'qa_source_crop_rgb_mismatch',f)
    xy=mapping['destinationXY']
    if len(xy)!=2 or not all(type(x) is int for x in xy) or not (0<=xy[0]<=canvas.width-crop.width and 0<=xy[1]<=canvas.height-crop.height): raise ValueError('Invalid integer QA destination: '+f)
    destination=(xy[0],xy[1],xy[0]+crop.width,xy[1]+crop.height)
    if covered.crop(destination).getbbox() is not None: raise ValueError('Overlapping QA source mappings: '+f)
    canvas.paste(crop,xy); covered.paste(1,destination)
    if key(sf)==key(archive):
     archive_mappings+=1
     if src.get('archiveContract')!=contract: self.issue(p,'qa_archive_contract_mismatch',f)
   if pixels.size!=canvas.size or pixels.tobytes()!=canvas.tobytes() or covered.getextrema()!=(1,1): self.issue(p,'qa_integer_reconstruction_mismatch',f)
   if hashlib.sha256(pixels.tobytes()).hexdigest()!=check.get('decodedRgbSha256'): self.issue(p,'qa_output_rgb_mismatch',f)
   if check.get('actuallyViewed') is not True or check.get('viewDetail')!='original': self.issue(p,'qa_missing_actual_original_view_claim',f)
  if not archive_mappings: self.issue(p,'qa_missing_archive_mapping',str(qa))
  return {'file':str(qa),'observedSha256':digest(qa),'historicallyHashBoundByGeneration':False,'actualViewClaims':len(checks),'integerReconstructionsVerified':len(self.issues)==start,'archiveSourceMappings':archive_mappings,'verified':len(self.issues)==start,'meaning':'Verifies stored review claims and exact source mappings; does not perform or invent new visual acceptance.'}
 def derived(self,r,p,entry,submitted):
  if r.get('route')!='local_native_processing': self.issue(p,'invalid_derived_route','Derived local operation must declare local_native_processing')
  if submitted.get('aiInvocation') is not False: self.issue(p,'missing_no_ai_invocation_declaration','submittedParameters.aiInvocation must be false')
  if any(k in submitted for k in ('prompt','referenced_image_paths','transparent_background')): self.issue(p,'forged_ai_submission_on_derived','Local operation must not masquerade as imagegen submission')
  if not r.get('generatedAtMeaning'): self.issue(p,'missing_derived_timestamp_meaning','Must distinguish local derivation time from original AI timestamps')
  # A source graph may be recorded as a flat derivedFrom list or as named
  # baseAI / repairAI / nativeNeighborSources. Both must carry real identities.
  named_sources=isinstance(r.get('nativeNeighborSources'),dict) and bool(r['nativeNeighborSources']) and all(isinstance(r.get(n),dict) and isinstance(r[n].get('image'),dict) for n in ('baseAI','repairAI'))
  if not r.get('operation') or not (r.get('derivedFrom') or named_sources): self.issue(p,'missing_derivation_description','Need explicit operation and flat or named source identity graph')
  # A delivery manifest is supporting metadata, not a new pixel source. Its
  # current hash may be observed without claiming it was historically bound,
  # provided its named output exactly matches the already SHA-bound source PNG.
  entry['metadataObservations']=[]
  for source in r.get('derivedFrom',[]):
   if not isinstance(source,dict) or not source.get('deliveryRecord') or source.get('deliveryRecordSha256'): continue
   meta=Path(source['deliveryRecord']); sp=source.get('path') or source.get('file'); sh=source.get('sha256')
   if not self.check(sp or '',sh,p,'delivery-associated source PNG'): continue
   delivery=self.load(meta,p)
   if not isinstance(delivery,dict): continue
   matches=[o for o in delivery.get('outputs',{}).values() if isinstance(o,dict) and key(o.get('path') or o.get('file') or '')==key(sp) and o.get('sha256')==sh]
   if not matches:
    self.issue(p,'delivery_output_identity_mismatch',f'{meta} does not name bound PNG {sp} / {sh}'); continue
   observation={'metadataPath':str(meta),'observedSha256':digest(meta),'observedAtAuditUtc':datetime.now(timezone.utc).isoformat(),'historicallyHashBound':False,'boundSourcePng':{'path':sp,'sha256':sh},'deliveryOutputSemanticallyMatches':True,'note':'Supporting metadata hash observed now. Pixel source retains its recorded full SHA binding; no claim that this metadata checksum was bound at generation time.'}
   self.observed_metadata[key(meta)]=observation; entry['metadataObservations'].append(observation)
  for name in ('baseAI','repairAI'):
   node=r.get(name)
   if not isinstance(node,dict): self.issue(p,'unsupported_derived_ai_link_schema',f'Missing structured {name}. Adapt explicitly; no guessed pass.'); continue
   img=node.get('image',{}); gen=node.get('generationRecord',{})
   if not isinstance(img,dict) or not isinstance(gen,dict): self.issue(p,'invalid_derived_ai_link',name); continue
   self.check(img.get('path',''),img.get('sha256'),p,name+' image')
   if self.check(gen.get('path',''),gen.get('sha256'),p,name+' generation record'):
    child=gen['path']; entry['children'].append(child); self.record(child,img.get('path'))
  evidence=r.get('processingEvidence')
  if not isinstance(evidence,dict): self.issue(p,'unsupported_processing_evidence_schema','Missing structured processingEvidence'); return
  for name in ('processing','localReview'):
   node=evidence.get(name,{})
   if not isinstance(node,dict) or not self.check(node.get('path',''),node.get('sha256'),p,name): continue
   j=self.load(node['path'],p)
   if j:
    self.inspect_links(j,p)
    if name=='processing': entry['processingRecord']=node; entry['processingOperation']=j.get('operation'); entry['processingLimits']=j.get('limits')
    else:
     entry['reviewRecord']=node
     views=j.get('actualViews')
     explicit_views=isinstance(views,list) and bool(views) and all(isinstance(v,dict) and v.get('actuallyViewed') is True and pathlike(v.get('file') or v.get('path')) and isinstance(v.get('sha256'),str) and HEX.fullmatch(v['sha256']) for v in views)
     entry['visualReviewClaimPresent']=bool(j.get('actualOriginalPixelViews') or j.get('actualViewCount') or explicit_views)
     if not entry['visualReviewClaimPresent']: self.issue(p,'missing_actual_view_claim','Review must document actual visual inspection; export statistics alone are insufficient')
  technical=evidence.get('technicalArtifacts')
  if isinstance(technical,list) and technical:
   # Combined NPZ stores RGB and exact native dx/dy fields in the canopy schema.
   # Do not demand a separate optical-flow file when that operation was not used.
   masks=[]; fields=[]
   for asset in technical:
    if not isinstance(asset,dict): self.issue(p,'invalid_technical_asset','Expected hashed asset object'); continue
    assetpath=asset.get('file') or asset.get('path')
    if not self.check(assetpath or '',asset.get('sha256'),p,'selected technical asset'): continue
    role=asset.get('role','').lower(); suffix=Path(assetpath).suffix.lower()
    if suffix=='.png' and 'mask' in role: masks.append(assetpath)
    if suffix=='.npz' and 'field' in role: fields.append(assetpath)
   if not masks or not fields: self.issue(p,'missing_processing_technical_asset','Named combined-field processing requires explicit hashed mask and NPZ field assets')
   entry['selectedTechnicalMasks']=masks; entry['selectedTechnicalFields']=fields
  else:
   for name in ('mask','flow'):
    node=evidence.get(name,{})
    if not isinstance(node,dict) or not self.check(node.get('path',''),node.get('sha256'),p,name):
     self.issue(p,'missing_processing_technical_asset',f'{name}: explicit hashed technical asset required; adapt if processing uses another field schema.')
  self.inspect_links(r,p,skip=('file',))
 def run(self,require_complete=False):
  # Index all explicit local hash references before resolving cross-linked evidence.
  generation_paths=set(self.tile.rglob('*generation*.json'))
  generation_paths.update(self.tile.glob('regional/generation.json'))
  for p in sorted(generation_paths):
   try: self.register_hashes(read(p))
   except Exception as exc: self.issue(p,'json_read_error',f'{type(exc).__name__}: {exc}')
  cells=[]; missing=[]
  for row in range(1,5):
   for col in range(1,5):
    cell=f'r{row:02}_c{col:02}'; p=self.tile/f'native/{cell}.png.generation.json'
    if not p.exists(): missing.append(cell); continue
    ent=self.record(p); cells.append({'cell':cell,**(ent or {'verified':False})})
  # Historical superseded/rejected calls count by actual source hash, not by files.
  for p in sorted(generation_paths):
   if key(p) in self.records: continue
   r=self.load(p,p)
   if isinstance(r,dict) and r.get('tool')=='image_gen.imagegen': self.record(p)
  # An unselected in-production repair can have a receipt before its sidecar is
  # written. Count it without promoting it to verified evidence or making it a
  # defect in an unrelated selected chain. A selected/derived missing sidecar
  # is already an explicit error when that required source graph is traversed.
  orphan_receipts=[]; pending_calls=[]
  for p in sorted(self.tile.rglob('*receipt*.json')):
   q=self.load(p,p)
   if not isinstance(q,dict) or not all(n in q for n in ('sourceOutputPath','prompt','references','generatedAt')): continue
   src=Path(q['sourceOutputPath'])
   if not src.is_file():
    self.issue(p,'missing_receipt_source_output',str(src)); continue
   try:
    sh=digest(src)
    with Image.open(src) as im: size=list(im.size); fmt=im.format
   except Exception as exc:
    self.issue(p,'receipt_source_read_error',f'{type(exc).__name__}: {exc}'); continue
   if sh in self.calls: continue
   cat='regional' if 'regional' in p.name or 'regional' in p.parts else 'native'
   self.calls[sh]={'sourceOutputSha256':sh,'sourceOutputPaths':[str(src)],'generationRecords':[],'receiptOnlyEvidence':{'path':str(p),'sha256':digest(p)},'categories':[cat],'sourcePixelsVerified':size==[1254,1254] and fmt=='PNG','recordStatuses':['pending-generation-record']}
   orphan_receipts.append(str(p)); pending_calls.append({'receipt':str(p),'receiptSha256':digest(p),'sourceOutputSha256':sh,'state':'in-production-unselected-receipt-only','completeGenerationEvidenceVerified':False,'selectionEvidence':False,'note':'Actual output counted once. Complete generation sidecar remains pending; no claim of acceptance or complete model/prompt/reference verification.'})
  bridges=[]
  for p in sorted(self.tile.glob('canopy-repair/*.manifest.json')):
   j=self.load(p,p)
   if not isinstance(j,dict): continue
   self.inspect_links(j,p)
   for _,path,h in self.pairs(j):
    if h in self.calls:
     bridges.append({'manifest':str(p),'manifestSha256':digest(p),'linkedSourcePath':path,'linkedSourceSha256':h,'recordStatusesPreserved':self.calls[h]['recordStatuses'],'role':'Actual manifest-linked guide/base relationship only; original review status is not changed.'})
  if require_complete and missing: self.issue(self.tile,'incomplete_native_grid',','.join(missing))
  nativecalls=[v for v in self.calls.values() if 'native' in v['categories']]
  regionalcalls=[v for v in self.calls.values() if 'regional' in v['categories']]
  return {'schemaVersion':2,'auditedAt':datetime.now(timezone.utc).isoformat(),'tile':str(self.tile),'tool':'verify_native_sources.py','readOnly':True,'wholeTileAccepted':False,'visualAcceptancePerformedByThisTool':False,'completeNativeGrid':not missing,'presentCellCount':len(cells),'missingCells':missing,'cells':cells,'distinctBuiltinNativeCallCount':len(nativecalls),'distinctBuiltinRegionalCallCount':len(regionalcalls),'nativeCallsWithVerifiedSourcePixels':sum(v['sourcePixelsVerified'] for v in nativecalls),'countMeaning':'Distinct actual sourceOutputSha256 values, including superseded / rejected ancestors and pending receipt-only calls; NOT count of selected cells or whole verified chains. Regional outputs counted separately. Derived local operations add zero builtin calls.','calls':list(self.calls.values()),'records':list(self.records.values()),'orphanReceiptsMissingGenerationRecords':orphan_receipts,'pendingInProductionCalls':pending_calls,'pendingFourthAttemptBridgeAssociations':bridges,'observedSupportingMetadata':list(self.observed_metadata.values()),'issues':self.issues,'allDiscoveredEvidenceVerified':not self.issues and not pending_calls,'selectionSourceReady':not missing and all(c['verified'] for c in cells) and not self.issues,'schemaPolicy':'Unknown required source / processing schemas fail explicit verification. sourceJob is optional; when absent, complete actual receipt and generation evidence suffice. Optional delivery metadata is separately marked observed-at-audit and semantically matched to the SHA-bound PNG, never claimed historically hash-bound. Archived image relocation requires exact pre-recorded SHA. Unselected receipt-only production calls are counted and marked pending, not accepted. Archive-dependent guides and recorded QA are reconstructed from exact archived pixels.'}

def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('tile'); parser.add_argument('--output'); parser.add_argument('--require-complete',action='store_true'); args=parser.parse_args()
 tile=Path(args.tile)
 if not tile.is_absolute(): tile=ROOT/tile
 tile=tile.resolve(strict=True)
 if not tile.is_relative_to(ROOT) or tile.parent!=ROOT: raise ValueError('Tile must be a direct child of production ROOT')
 result=Audit(tile).run(args.require_complete)
 if args.output:
  output=Path(args.output)
  if not output.is_absolute(): output=ROOT/output
  output=output.resolve()
  if not output.is_relative_to(ROOT): raise ValueError('Audit output escapes production ROOT')
  if output.exists(): raise FileExistsError('Existing audit is immutable: '+str(output))
  output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'tile':str(tile),'presentCellCount':result['presentCellCount'],'missingCellCount':len(result['missingCells']),'distinctBuiltinNativeCallCount':result['distinctBuiltinNativeCallCount'],'distinctBuiltinRegionalCallCount':result['distinctBuiltinRegionalCallCount'],'issueCount':len(result['issues']),'issueCodes':sorted({i['code'] for i in result['issues']}),'selectionSourceReady':result['selectionSourceReady'],'output':args.output},ensure_ascii=False,indent=2))
 return 0 if not result['issues'] else 2
if __name__=='__main__': raise SystemExit(main())
