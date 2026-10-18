from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production as p
q=p.ROOT/'qa'; index=q/'expansion-west-worker-map.json'; d=p.load(index)
added=['r09_c01_s03_04_v01','r09_c01_s04_04_v01','r09_c01_s01_03_v01','r09_c01_s02_03_v01','r09_c01_s03_03_v01','r09_c01_s04_03_v01']
records=[]
for stem in added:
    path=p.ROOT/'native'/f'{stem}.png'; rec=p.load(str(path)+'.generation.json')
    assert p.hashfile(path)==rec['sha256'] and rec['nativeSizeMatchesPlan']
    assert all(p.hashfile(x['path'])==x['sha256'] for x in rec['references'])
    assert p.hashfile(p.ROOT/'receipts'/f'{stem}.tool.json')==rec['receiptSha256']
    records.append({'stem':stem,'path':str(path),'sha256':rec['sha256'],'dimensions':[rec['width'],rec['height']],'coordinates':rec['coordinates'],'actualModel':None})
d['status']='waiting_builtin_network'; d['currentRequest']='r09_c01_s01_02_v01'
d['currentError']={'recordedAtUtc':p.now(),'tool':'image_gen.imagegen','request':'r09_c01_s01_02_v01','error':'image generation failed: network error: error sending request','receipt':str(p.ROOT/'receipts'/'r09_c01_s01_02_v01.tool.json'),'retries':0}
d['updatedAtUtc']=p.now(); p.dump(index,d)
d['candidateArtifacts']['r09_c02']['qaManifest']=str(q/'west-r09c02-bamboo-upper-v02-manifest.json')
d['candidateArtifacts']['r09_c02']['baseInternalReview']=str(q/'c04-hardseam-west-r09c02-v01-review.json')
p.dump(index,d)
checkpoint={'createdAtUtc':p.now(),'worker':'west','assignedTiles':d['assignedTiles'],'newSelectedCoreCount':len(added),'newSelectedCores':records,'selectedNativeCount':sum(bool(x) for t in d['assignedTiles'] for row in d[t] for x in row),'tileCoverage':{t:sum(bool(x) for row in d[t] for x in row) for t in d['assignedTiles']},'savedGenerationCount':d['generationCount'],'repairSources':['r09_c02_bamboo_upper_joint_v01','r09_c02_bamboo_upper_joint_v02'],'currentCandidateArtifacts':d['candidateArtifacts'],'networkFailure':d['currentError'],'pendingFailedCoordinate':'r09_c01_s01_02_v01','resumeInstruction':'Same coordinate requires a new request/receipt version v02, preserving v01 failed receipt. Do not regenerate the six saved cores.','formalAccepted':False,'mainIndexUnmodifiedByWorker':True,'sharedGitUnmodified':True}
p.dump(q/'west-resume-checkpoint-20261016.json',checkpoint)
print({'selected':checkpoint['selectedNativeCount'],'generated':d['generationCount'],'r09c01':checkpoint['tileCoverage']['r09_c01'],'checkpoint':str(q/'west-resume-checkpoint-20261016.json')})
