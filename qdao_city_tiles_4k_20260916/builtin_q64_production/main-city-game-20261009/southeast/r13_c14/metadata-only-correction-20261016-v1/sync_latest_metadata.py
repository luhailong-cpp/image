"""One-time metadata-only synchronization; all art and historic evidence immutable."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,shutil
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent.parent
Z=T.parent
OUT=Path(__file__).resolve().parent
def require(ok,message):
    if not ok: raise ValueError(message)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def write_new(p,d):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
def checked(entry):
    p=Path(entry['path'])
    require(sha(p)==entry['sha256'],'Evidence changed: '+str(p))
    return p
def copy_new(src,dst):
    with Path(src).open('rb') as r,Path(dst).open('xb') as w:shutil.copyfileobj(r,w)
    require(sha(src)==sha(dst),'Backup/copy mismatch')
    return ref(dst)

census_path=Z/'batch-checkpoints/resume-census-20261016-v2.json'
census=read(census_path)
conflict=census['r13c14SelectionConflict']
require(conflict['tile']==T.name=='r13_c14','Scope mismatch')
progress_path=T/'progress.json'
latest_path=T/'candidate/latest-assembly.json'
evidence=conflict['evidence']
for item in evidence.values():checked(item)
p=read(progress_path)
old=read(latest_path)
retained=conflict['retainedCandidate'];context=conflict['retainedContext']
stale=conflict['staleCandidate'];oldcontext=conflict['staleContext']
for item in [retained,context,stale,oldcontext]:checked(item)
require(p['candidate']==retained['path'] and p['candidateSha256']==retained['sha256'],'Progress candidate differs')
require(p['context']==context['path'] and p['contextSha256']==context['sha256'],'Progress context differs')
require(old['candidate']['sha256']==stale['sha256'] and old['context']['sha256']==oldcontext['sha256'],'Latest no longer stale as audited')
composition_path=checked(evidence['composition'])
composition=read(composition_path)
require(p['repairManifest']==str(composition_path),'Progress repair manifest differs')
for key,entry in [('candidate',retained),('context',context)]:
    require(composition[key]['path']==entry['path'] and composition[key]['sha256']==entry['sha256'],'Composition output mismatch')
local_qa=read(checked(evidence['localQA']))
rejected_qa=read(checked(evidence['laterRejectedQA']))
continuation=read(checked(evidence['continuation']))
require(local_qa['status']=='local_pass' and local_qa['formalAccepted'] is False,'Unexpected local QA')
require(rejected_qa['status']=='rejected' and rejected_qa['activeCandidateUnchanged']['sha256']==retained['sha256'],'Later attempt changed selected candidate')
require(continuation['firstActualNewOutputReview']['status']=='rejected' and continuation['currentCandidate']['sha256']==retained['sha256'],'Continuation selection differs')
require(p['status']=='candidate_west_parasol_geometry_failed' and p['formalAccepted'] is False,'Current unresolved state differs')
require(conflict['pixelDependencyComparisonNotVisualQA']['changedBox']==[0,1154,627,2401],'Census changed box differs')
require(len(conflict['downstreamDependencies'])==8 and all(d['samePixelsInRetainedContext'] for d in conflict['downstreamDependencies']),'Missing downstream pixel audit')
for d in conflict['downstreamDependencies']:checked(d['generationRecord'])
# Paired output check is numeric only, not visual acceptance.
with Image.open(retained['path']) as im:
    require(im.size==(4096,4096),'Candidate size mismatch')
    core=np.asarray(im.convert('RGB'))
with Image.open(context['path']) as im:
    require(im.size==(4326,4326),'Context size mismatch')
    require(np.array_equal(core,np.asarray(im.convert('RGB'))[115:4211,115:4211]),'Current core/context pairing differs')
protected_paths=[Path(i['path']) for i in evidence.values() if Path(i['path'])!=latest_path]
protected_paths += [Path(i['path']) for i in [retained,context,stale,oldcontext]]
protected_paths += [T/'active-native-map.json',Path(p['localContinuation']),Path(old['manifest']['path'])]
protected_paths += [Path(d['generationRecord']['path']) for d in conflict['downstreamDependencies']]
protected={str(x):sha(x) for x in protected_paths}
require(sha(old['manifest']['path'])==old['manifest']['sha256'],'Historic base manifest changed')
# Back up both mutable entrypoints before changing the latest wrapper.
latest_backup=copy_new(latest_path,OUT/'latest-assembly-before.json')
progress_backup=copy_new(progress_path,OUT/'progress-before.json')
stamp=datetime.now(timezone.utc).isoformat()
after={
    'schemaVersion':2,'tile':T.name,'updatedAt':stamp,
    'status':p['status'],'formalAccepted':False,
    'internalArtQA':p['internalArtQA'],'externalNeighborSeamQA':p['externalNeighborSeamQA'],
    'candidate':composition['candidate'],'context':composition['context'],
    'manifest':ref(composition_path),'repairManifest':ref(composition_path),
    'baseAssembly':{'manifest':old['manifest'],'assemblyIdentitySha256':old['assemblyIdentitySha256'],
                    'scope':'Original sixteen-native assembly before retained west local repairs; preserved as lineage only'},
    'localQA':{**evidence['localQA'],'status':local_qa['status'],
               'scope':'Retained W3a grout repair and its perimeters only; parasol defects and other pending QA remain'},
    'selectionAuthority':{'progress':ref(progress_path),'continuation':evidence['continuation'],
                          'laterRejectedQA':evidence['laterRejectedQA'],
                          'reason':'Current progress, retained repair composition, local review, and rejected followup explicitly retain89c0'},
    'metadataOnlyCorrection':{'record':str(OUT/'metadata-only-correction.json'),
                              'previousWrapper':latest_backup,'progressBackup':progress_backup,
                              'artPixelsChanged':False,'newArtAcceptanceGranted':False},
}
version_path=OUT/'latest-assembly-corrected.json'
write_new(version_path,after)
require(sha(latest_path)==evidence['wrapper']['sha256'] and sha(progress_path)==evidence['progress']['sha256'],'Entrypoint changed before write')
for filename,digest in protected.items():require(sha(filename)==digest,'Protected input changed before metadata mutation: '+filename)
temp=latest_path.with_name('latest-assembly.metadata-correction-20261016-v1.tmp')
copy_new(version_path,temp)
os.replace(temp,latest_path)
require(read(latest_path)==after and sha(latest_path)==sha(version_path),'Latest synchronization mismatch')
for filename,digest in protected.items():require(sha(filename)==digest,'Protected input changed after metadata mutation: '+filename)
record={
    'schemaVersion':1,'tile':T.name,'completedAt':datetime.now(timezone.utc).isoformat(),
    'operation':'metadata_only_latest_wrapper_sync_to_preexisting_current_progress',
    'status':'completed_no_art_or_QA_reclassification','formalAccepted':False,
    'reason':conflict['conclusion'],
    'backups':{'latest':latest_backup,'progress':progress_backup},
    'beforeLatest':evidence['wrapper'],'afterLatest':ref(latest_path),'immutableCorrectedWrapper':ref(version_path),
    'progressUnchanged':True,'progress':ref(progress_path),'selectedCandidate':retained,'selectedContext':context,
    'selectedComposition':evidence['composition'],'selectedLocalQA':evidence['localQA'],
    'selectionContinuation':evidence['continuation'],'laterRejectedQA':evidence['laterRejectedQA'],
    'census':ref(census_path),'currentCoreExactlyMatchesContextCrop':True,
    'reusedPixelDependencyAudit':{'source':ref(census_path),'section':'r13c14SelectionConflict',
                                'allRelevantInputHashesVerifiedUnchanged':True,
                                'comparison':conflict['pixelDependencyComparisonNotVisualQA'],
                                'downstreamDependencyCount':8,'downstreamDependencies':conflict['downstreamDependencies']},
    'retainedStatus':p['status'],'retainedInternalArtQA':p['internalArtQA'],
    'retainedExternalNeighborSeamQA':p['externalNeighborSeamQA'],'retainedPending':conflict['pending'],
    'protectedFilesUnchanged':[{'path':name,'sha256':digest} for name,digest in protected.items()],
    'writeScope':{'replacedExistingFiles':[str(latest_path)],'newFilesDirectory':str(OUT),
                  'progressChanged':False,'pngChanged':False,'oldManifestOrQAChanged':False,
                  'otherTilesChanged':False,'gitOperated':False},
    'script':ref(__file__),
}
write_new(OUT/'metadata-only-correction.json',record)
print(json.dumps({'status':record['status'],'latest':ref(latest_path),'record':ref(OUT/'metadata-only-correction.json'),
                  'progressUnchanged':True,'candidateSha256':retained['sha256'],'contextSha256':context['sha256']},indent=2))
