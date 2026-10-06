from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;TILE=OUT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return {'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def external_refs():
 found={};prefix=str(TILE.resolve()).lower()+'\\'
 def walk(x,record):
  if isinstance(x,dict):
   for v in x.values():walk(v,record)
  elif isinstance(x,list):
   for v in x:walk(v,record)
  elif isinstance(x,str) and len(x)<400 and x.lower().endswith('.png') and '\n' not in x:
   p=Path(x)
   if p.is_absolute():
    full=str(p.resolve())
    if full.lower().startswith(prefix):found.setdefault(full,[]).append(str(record))
 for sibling in TILE.parent.iterdir():
  if not sibling.is_dir() or sibling.resolve()==TILE.resolve():continue
  for record in sibling.rglob('*.json'):
   try:walk(load(record),record)
   except (json.JSONDecodeError,UnicodeDecodeError):pass
 return [{'file':p,'exists':Path(p).exists(),'sha256':sha(p) if Path(p).exists() else None,'referencingRecords':sorted(set(rs)),'retention':'Conservative live external record reference; retain during cleanup'} for p,rs in sorted(found.items())]
def main():
 dest=OUT/'delivery.manifest.json';assert not dest.exists(),'Do not overwrite an existing selection'
 now=datetime.now(timezone.utc).isoformat();rootp=TILE/'qa/root-final-review.json';assert sha(rootp)=='2e4af772fbf51b1d9fde7c42e6e22648f2219ae9fc9b23d8da5a3691b2fa68a8';root=load(rootp)
 assert root['coverage']['allExportedScopesCoveredByActualViewsAndByteIdentity'] and root['coverage']['exportedTotal']==89 and root['coverage']['actualOriginalPixelImagesViewedAcrossTeam']==85
 assert all(not c['requiresRepair'] for c in root['newRootOriginalPixelChecks'])
 for r in root['reports']:assert sha(r['file'])==r['sha256']
 a=load(TILE/'candidate/assembly.manifest.json');corep=TILE/'candidate/core4096.png';extp=TILE/'candidate/extended4326.png'
 assert sha(corep)=='0cefa2ece52b708f6b7021bfa878d466451cc1a0fd337cc9679754e949686c8b';assert sha(extp)=='9f4279c1fec0ff91aa62fcb21e2fcb3e78ca021266732ed6096adb9338e341f5'
 core=np.array(Image.open(corep));ext=np.array(Image.open(extp));assert core.shape==(4096,4096,3) and ext.shape==(4326,4326,3);assert np.array_equal(core,ext[115:4211,115:4211])
 reconstructedCore=np.empty_like(core);reconstructedExtended=np.empty_like(ext);coverage=np.zeros(ext.shape[:2],np.uint8);native=[];selectedReceipts=[];sourceOutputs=set()
 mappings={m['cell']:m for m in a['pixelMappings']}
 for src in a['derivedFrom']:
  p=Path(src['file']);gp=Path(src['generationRecord']);assert sha(p)==src['sha256'];assert sha(gp)==src['generationRecordSha256'];g=load(gp);assert g['sha256']==src['sha256'] and g['actualModel'] is None and g['actualQuality'] is None
  im=np.array(Image.open(p));assert im.shape==(1254,1254,3);m=mappings[src['cell']];x0,y0,x1,y1=m['sourceBox'];dx,dy=m['extendedDestinationXY'];reconstructedExtended[dy:dy+y1-y0,dx:dx+x1-x0]=im[y0:y1,x0:x1];coverage[dy:dy+y1-y0,dx:dx+x1-x0]+=1
  x0,y0,x1,y1=m['coreSourceBox'];dx,dy=m['coreDestinationXY'];reconstructedCore[dy:dy+y1-y0,dx:dx+x1-x0]=im[y0:y1,x0:x1]
  for pk,hk in [('prompt','promptSha256'),('sourceJob','sourceJobSha256')]:assert sha(g[pk])==g[hk],(src['cell'],pk)
  e=g['evidence'];assert sha(e['toolResultPath'])==e['toolResultSha256'];assert sha(e['sourceOutputPath'])==src['sha256'];sourceOutputs.add(str(Path(e['sourceOutputPath']).resolve()).lower())
  references=[]
  for rr in g['references']:
   rp=Path(rr['path']);assert rp.exists() and sha(rp)==rr['sha256'],rp;references.append({**rr,'hashVerifiedAtSelection':True})
  receipt=TILE/'jobs'/(src['cell']+'.receipt.json');assert receipt.exists();rd=load(receipt);assert str(Path(rd['sourceOutputPath']).resolve()).lower()==str(Path(e['sourceOutputPath']).resolve()).lower()
  selectedReceipts.append(ref(receipt));native.append({**src,'identityAndEvidence':{k:g.get(k) for k in ['generatedAt','tool','route','configSnapshot','submittedParameters','actualModel','actualQuality','unverifiedReason','evidence','prompt','promptSha256','sourceJob','sourceJobSha256']},'actualReceipt':ref(receipt),'references':references,'nativeSourceAndAllEvidenceHashesVerified':True,'sourcePixelsCopiedExactly':True,'retention':'Selected game output supersedes nativePNG; source/generation/receipt/prompt/reference text retained'})
 assert len(native)==16 and len(sourceOutputs)==16 and np.all(coverage==1)
 assert np.array_equal(core,reconstructedCore) and np.array_equal(ext,reconstructedExtended)
 rejected=[]
 for rp in sorted((TILE/'jobs').glob('*.attempt*.receipt.json')):
  d=load(rp);sp=Path(d['sourceOutputPath']);assert sp.exists();ss=sha(sp);size=list(Image.open(sp).size);assert size==[1254,1254];assert str(sp.resolve()).lower() not in sourceOutputs
  if 'sourceOutputSha256' in d:assert d['sourceOutputSha256']==ss
  refs=[]
  for rr in d['references']:
   pp=Path(rr['path']);assert pp.exists();hh=sha(pp)
   if 'sha256' in rr:assert rr['sha256']==hh
   refs.append({**rr,'sha256':hh,'hashVerifiedAtSelection':True})
  rejected.append({'cell':rp.name.split('.attempt')[0],'receipt':ref(rp),'sourceOutput':ref(sp),'nativePixels':size,'generatedAt':d['generatedAt'],'prompt':d['prompt'],'promptUtf8Sha256':hashlib.sha256(d['prompt'].encode('utf-8')).hexdigest(),'references':refs,'actualModel':d.get('actualModel'),'actualQuality':d.get('actualQuality'),'status':d['status'],'reason':d['reason'],'inSelectedAssembly':False,'reviewEvidence':'Receipt rejection status and worker row observation; source output remains outside tile and is not deleted by this scoped cleanup'})
 assert len(rejected)==2 and {r['cell'] for r in rejected}=={'r01_c03','r03_c02'}
 receipts=list((TILE/'jobs').glob('*.receipt.json'));assert len(receipts)==18
 audit={'createdAtUtc':now,'nativeBuiltinCallsWithDistinctRecordedOutput':18,'selectedNativeImages':16,'rejectedNativeOutputs':2,'rejectedByRow':{'row01':1,'row03':1},'countMethod':'16 selected generation records and matching receipts/source-output hashes, plus2 distinct attempt receipts/output hashes. Each actual output file was readable and1254square. Regional generation counted separately.','selectedReceiptEvidence':selectedReceipts,'rejected':rejected,'allNativeActualModelQualityNull':True}
 write(OUT/'native-call-audit.json',audit)
 regional=load(TILE/'regional/generation.json');assert sha(regional['file'])==regional['sha256'];regionalEvidence={'generation':ref(TILE/'regional/generation.json'),'toolResult':ref(TILE/'regional/tool-result.json'),'review':ref(TILE/'regional/visual-review.json'),'source':ref(regional['file']),'identityAndEvidence':regional,'role':'Separate regional composition/reference only, not one of16 native cores and not enlarged into the4096 output','additionalRegionalCallCount':1}
 proof={'createdAtUtc':now,'coreExactlyCenterCrop':True,'all16CoreMappingsExactlyNativePixels':True,'all16ExtendedMappingsExactlyNativePixels':True,'extendedCoverageEveryPixelExactlyOnce':True,'nativeDimensions':[1254,1254],'productionAssemblyResampling':'none','postAssemblyFlowApplied':False,'postAssemblyToneApplied':False,'postAssemblyNativeAIPatchesApplied':False,'selectedCopyByteIdenticalToCandidate':True,'rootReviewHashVerified':True,'allReferencedTeamReviewHashesVerified':True,'coreLeft230RawRGBSha256':hashlib.sha256(core[:,:230].tobytes()).hexdigest(),'extendedLeft230RawRGBSha256':hashlib.sha256(ext[:,:230].tobytes()).hexdigest(),'earlyNorthSourceUnchanged':root['earlyNorthInheritance']['northSelectedSourceUnchanged'],'earlyNorthTop1024Exact':root['earlyNorthInheritance']['first1024RowsRawRgbIdentical'],'earlyVerticalTop3072Exact':root['earlyVerticalReview']['first3072RowsRawRgbIdentical']}
 outputs={}
 for role,name in [('core','core4096.png'),('extended','extended4326.png'),('preview','preview1024.png')]:
  src=TILE/'candidate'/name;dst=OUT/name;assert not dst.exists();assert sha(src)==a['outputs'][role]['sha256'];shutil.copyfile(src,dst);assert sha(dst)==sha(src);outputs[role]={**ref(dst),'pixels':list(Image.open(dst).size),'productionPixels':role!='preview'}
 write(OUT/'selection-proof.json',proof)
 consumers=external_refs();write(OUT/'external-consumer-audit.json',{'checkedAtUtc':now,'scanScope':'JSON records under sibling tile directories, excluding this tile; conservative exact localPNG path references','references':consumers,'futureConsumerPolicy':'r09_c09 and later consumers must reference selected/core4096 or selected/extended4326; candidate is superseded'})
 northActive=[ref(TILE.parent/'r08_c10/west-repair/v3/core4096.png'),ref(TILE.parent/'r08_c10/west-repair/v3/extended4326.png')]
 manifest={'schemaVersion':1,'createdAtUtc':now,'tile':'r09_c10','status':'qualified_complete_4k_candidate_pending_remaining_adjacent_edges_and_formal_acceptance','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'runtimePublished':False,'geometry':a['geometry'],'pixelRectXYWH':[36864,32768,4096,4096],'outputs':outputs,'selectionProof':ref(OUT/'selection-proof.json'),'sourceChain':{'assembly':ref(TILE/'candidate/assembly.manifest.json'),'rawCore':ref(corep),'rawExtended':ref(extp),'nativeSources':native,'rejectedNativeEvidence':ref(OUT/'native-call-audit.json'),'regionalSeparate':regionalEvidence,'northCurrentSelected':ref(TILE.parent/'r08_c10/selected/core4096.png'),'northHistoricalActiveGenerationDependenciesPreservedOutsideCleanupScope':northActive},'nativeCounts':{'selected':16,'rejected':2,'actualNativeCalls':18,'regionalCallsSeparately':1,'countAudit':ref(OUT/'native-call-audit.json')},'processingDeclaration':{'nativeRoute':'builtin image_gen.imagegen','configuredTarget':{'model':'gpt-image-2.5-sunburst','quality':'max'},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'modelQualityEvidence':'Host-managed tool has no explicit model/quality selectors or verified returned identity; configured/prompted targets are not actual backend proof. Per-image records retained.','nativeSourceCreation':'16 actual native1254x1254 selected outputs plus2 rejected native trials; rejected outputs were not assembled','regionalUse':'One separate1254 regional reference. Native details were newly generated; regional reference was not enlarged as final artwork.','assembly':'Exact integer crop/paste of source-native pixels into4326 extended and4096 core; every source mapping independently verified','noNativeEnlargement':True,'productionScaling':False,'postAssemblyFlow':False,'postAssemblyToneCorrection':False,'postAssemblyAIPatch':False,'blur':False,'feather':False,'registration':False,'productionResampling':'none','preview':'1024 LANCZOS downsample for overview only, not production pixels or pixel-level QA evidence','selection':'Byte-identical copy of original candidate files, no new image processing'},'qaSummary':{'rootFinalReview':ref(rootp),'rootCoverage':root['coverage'],'exportedScopes':89,'actualOriginalPixelViewsAcrossTeam':85,'coverageDifference':'Four own-north exports are strictly covered as exact lower256-row halves of four actual512-row external north joins; no redundant views claimed','inheritance':{'earlyVertical':root['earlyVerticalReview'],'earlyNorth':root['earlyNorthInheritance']},'teamReports':root['reports'],'rootNewChecks':root['newRootOriginalPixelChecks'],'overview':root['overview'],'allExportedScopesCoveredByActualViewsAndByteIdentity':True,'remainingHorizontalAndOuterReviewsPass':True,'noNewRepairRequired':True,'scopeLimit':'Listed89 exported scopes covered by85 actual native views and verified crop identity, plus overview. Not a claim that every pixel or future neighbor is formally accepted.'},'futureEastReferenceForR09C09':{'core':outputs['core'],'extended':outputs['extended'],'coreLeft230RawRGBSha256':proof['coreLeft230RawRGBSha256'],'extendedLeft230RawRGBSha256':proof['extendedLeft230RawRGBSha256'],'useSelectedOnly':True,'westNeighborSeamNotYetValidated':True},'remaining':[{'kind':'minor_material_variation','details':root['knownMinorResiduals']},{'kind':'adjacent_edges','edges':['west','east','south'],'description':'Not yet generated or jointly accepted; own-edge QA is not external seam acceptance.'},{'kind':'four_tile_corner_junctions','description':'Four-way neighboring tile junctions remain unverified.'},{'kind':'formal_client_whole_city','description':'Formal art acceptance, client loading/navigation, runtime publication and whole-city completion remain false.'}],'retention':{'state':'selected_verified_cleanup_pending','keep':'selected all; actual external consumers referencedPNG; technical masks if any; all nonPNG records/data','noInventedMasks':True,'deleteScope':'Superseded PNG only within resolved r09_c10 tree. No cross-tile or generated_images deletion.','northWESTv3':'Both r08_c10 WESTv3 sourcePNG explicitly remain untouched outside this scope','externalConsumerAudit':ref(OUT/'external-consumer-audit.json'),'historicalReferencePolicy':'Removed PNG paths remain provenance with original hashes in records and per-file cleanup ledger; never rewrite them as another source.'}}
 write(dest,manifest);print(json.dumps({'outputs':outputs,'deliveryManifest':ref(dest),'nativeCalls':18,'selectedNative':16,'rejected':2,'regionalSeparate':1,'externalConsumers':consumers}))
if __name__=='__main__':main()
