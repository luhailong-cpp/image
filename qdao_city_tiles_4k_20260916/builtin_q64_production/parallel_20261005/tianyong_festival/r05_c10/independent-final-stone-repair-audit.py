from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
B=Path(__file__).parent;D=B/'final-stone-clean-v1';F=D/'final-v1'
R=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':H(p)}
A=lambda p:np.array(Image.open(p).convert('RGBA'))
def refs(o):
 if isinstance(o,dict):
  if 'file' in o and 'sha256' in o:yield o
  for v in o.values():yield from refs(v)
 elif isinstance(o,list):
  for v in o:yield from refs(v)
def verify(o):
 for r in refs(o):assert H(r['file'])==r['sha256'],r
oldp=B/'independent-full-chain-audit.json'
assert H(oldp)=='6838906976bf5e64c0c580f8ce7872ff87ebacf0876fd877e79cfb03a9fe5270'
old=R(oldp)
assert H(B/'independent-provenance-clarifications.json')=='e6ba2b0fbb3c7b649b6911b7a3b71af4a30e79cd50a5aaf3342312805162cee2'
mp=F/'manifest.json';m=R(mp)
assert H(mp)=='a6255db45f8e631ace4b16c6a7f578aea1ad01c04ccc39d9c2b6715e68870bf4'
cp=R(B/'local-source-checkpoint.json');asm=R(F/'assembly.json');g=R(D/'native.png.generation.json');prep=R(D/'preparation.json')
for x in [m,cp,asm,g,prep,R(F/'visual-review.json'),R(F/'r05_c10-fragment.png.generation.json')]:verify(x)
assert cp['manifest']==ref(mp)
assert m['requiresPriorManifest']==old['entries'][-1]['manifest']
prior_snapshot_text=(D/'source-checkpoint-input.json').read_text(encoding='utf-8-sig')
prior_original_bytes=(prior_snapshot_text.rstrip('\r\n').replace('\r\n','\n').replace('\n','\r\n')+'\r\n').encode('utf8')
assert hashlib.sha256(prior_original_bytes).hexdigest()==old['localSourceCheckpoint']['sha256']
assert len(m['patches'])==1
p=m['patches'][0];box=p['destinationTileLTRB'];crop=p['cropFromJoinedLTRB']
assert box==[1830,1940,2190,2110] and crop==[360,490,720,660]
assert p['requiredPriorSource']==old['finalFragment'] and asm['finalSource']==old['finalFragment']
assert cp['fragment']==asm['candidate']
assert cp['coupledBottom']==old['finalCoupled06']
assert m['windowTileLocalLTRB']==[1470,1450,2724,2704] and m['windowGlobalLTRB']==[38334,17834,39588,19088]
base=A(p['requiredPriorSource']['file']);final=A(cp['fragment']['file']);joined=A(m['joined']['file']);asset=A(p['asset']['file']);source=A(asm['context']['file']);native=A(asm['native']['file'])
assert final.shape==(4096,4096,4) and np.all(final[:,:,3]==255)
assert native.shape==(1254,1254,4)
assert np.array_equal(source,base[1450:2704,1470:2724])
assert np.array_equal(asset,joined[490:660,360:720])
recon=base.copy();recon[1940:2110,1830:2190]=asset
assert np.array_equal(recon,final)
diff=np.any(base!=final,axis=2);yy,xx=np.where(diff)
bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
assert int(diff.sum())==48226 and bb==[1834,1944,2187,2103]
owned=np.zeros((4096,4096),bool);owned[1940:2110,1830:2190]=True
assert not np.any(diff[~owned])
# Verify the entire 1254 native assembly is the documented same-position source blend.
y,x=np.indices((1254,1254))
def sm(v):v=np.clip(v,0,1);return v*v*(3-2*v)
W=sm((x-360)/30)*(1-sm((x-680)/40))*sm((y-490)/35)*(1-sm((y-625)/35))
expected=np.rint(source[:,:,:3]*(1-W[:,:,None])+native[:,:,:3]*W[:,:,None]).astype('uint8')
assert np.array_equal(expected,joined[:,:,:3])
assert np.array_equal(np.rint(W*255).astype('uint8'),np.array(Image.open(asm['sourceWeight']['file'])))
assert asm['nativeScale']==1 and asm['noUpscale'] and not asm['registrationApplied'] and not asm['toneCorrectionApplied']
for k in ['actualSubmittedModel','actualSubmittedQuality','actualReturnedModel','actualReturnedQuality']:assert g[k] is None
assert g['actualReturnedPixels']==[1254,1254]
assert g['observedCompletionAtUtc']=='2026-10-09T04:23:37.818267+00:00'
assert g['output']==asm['native'] and g['source']['sha256']==g['output']['sha256']
assert g['configTarget']['model']=='gpt-image-2.5-sunburst' and g['configTarget']['quality']=='max'
panels=[];unchanged=[];changed=[]
for r,y in enumerate([0,1280,2560],1):
 for c,x in enumerate([0,1280,2560],1):
  name=f'overlap-r{r}-c{c}-1536.png';op=B/'full-tile-qa'/name;npth=B/'full-tile-qa-final'/name
  oa=A(op);na=A(npth)
  assert np.array_equal(oa,base[y:y+1536,x:x+1536]) and np.array_equal(na,final[y:y+1536,x:x+1536])
  same=H(op)==H(npth)
  (unchanged if same else changed).append(name)
  panels.append({'name':name,'prior':ref(op),'final':ref(npth),'sameFileSHA':same,'nativeCropMatchesBoundSource':True})
assert len(unchanged)==8 and changed==['overlap-r2-c2-1536.png']
south=[]
for i in range(1,4):
 name=f'south-overlap-{i}-native.png';op=B/'full-tile-qa'/name;npth=B/'full-tile-qa-final'/name
 assert H(op)==H(npth)
 south.append({'prior':ref(op),'final':ref(npth),'sameFileSHA':True})
index=R(B/'full-tile-qa-final/inspection-index.json');verify(index)
assert index['source']==cp['fragment'] and index['southSource']==cp['coupledBottom']
out={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'auditor':'/root/continue_north/audit05','scope':'Independent read-only audit of seventeenth native repair and final QA panel inheritance. No old audit, old record, image, root or current state modified.','passed':True,'baseSixteenManifestAudit':ref(oldp),'baseProvenanceClarifications':ref(B/'independent-provenance-clarifications.json'),'priorCheckpointPreservedExactAt':ref(D/'source-checkpoint-input.json'),'currentLocalSourceCheckpoint':ref(B/'local-source-checkpoint.json'),'appendedManifest':ref(mp),'manifestCountAfterAppend':17,'baseFragment':p['requiredPriorSource'],'finalFragment':cp['fragment'],'coupled06Unchanged':cp['coupledBottom'],'destinationROI':box,'actualChangedPixels':48226,'actualChangedTileLocalLTRB':bb,'allPixelsOutsideROIExact':True,'appendedPatchReconstructionExact':True,'assetIsExactJoinedCrop':True,'nativeAssemblyReconstructionExactWithoutResampling':True,'sourceNativeIsExactBaseCrop':True,'fullOpaquePixelCoverage':16777216,'newNativeGenerationRecord':ref(D/'native.png.generation.json'),'observedCompletionAtUtc':g['observedCompletionAtUtc'],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'modelQualityTargetNotTreatedAsActual':True,'wholeTileQAPanels':panels,'unchangedWholeTilePanelCount':8,'changedWholeTilePanels':changed,'southQAPanels':south,'allSouthPanelsUnchanged':True,'finalInspectionIndex':ref(B/'full-tile-qa-final/inspection-index.json'),'openAuditFindings':[],'visualAcceptance':'Not assessed independently here; parent performs final native visual QA.','formalAccepted':False,'rootPublished':False}
out['priorCheckpointSnapshot']=out.pop('priorCheckpointPreservedExactAt')
out['priorCheckpointSerializationNote']='Snapshot JSON content matches audited checkpoint; re-encoding snapshot as UTF-8 without BOM, CRLF and one trailing newline reproduces original checkpoint SHA exactly. Snapshot own SHA differs only due newline serialization.'
out['priorCheckpointReconstructedOriginalSHA']=hashlib.sha256(prior_original_bytes).hexdigest()
op=B/'independent-final-stone-repair-audit.json';assert not op.exists();op.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'audit':ref(op),'final':cp['fragment'],'actualChangedPixels':48226,'unchangedWholeQAPanels':8,'changedWholeQAPanel':changed[0],'southPanelsUnchanged':True}))

