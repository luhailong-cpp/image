from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import production as p
prefix='c04-hardseam-east-r09c06-v01'
rp=R/'qa'/f'{prefix}-report.json';report=p.load(rp)
notes={'tile':'r09_c06','reviewedAtUtc':p.now(),'status':'complete native 4K candidate; three short paving notches require repair','stablePrefix':prefix,'reviewedNativeStrips':24,'reviewedNativeJunctions':9,'reviewScale':'all 24 strip views and 9 junction views inspected at 1:1, 1254 preview only for layout','rawReviewManifest':str(R/'qa'/f'{prefix}-native-QA-manifest.json'),'remainingInternalIssues':[{'tileLocalBox':[900,500,1050,610],'issue':'diagonal paving grout doubles/ends near first vertical overlap','kind':'geometry'},{'tileLocalBox':[900,900,1070,1060],'issue':'diagonal paving grout ends near upper-left 1024 junction','kind':'geometry'},{'tileLocalBox':[3120,1140,3260,1270],'issue':'short diagonal grout dead end in original s02_04 overlap','kind':'geometry'}],'materialNotes':['Native stone brush mark density becomes finer and golden grout stronger toward eastern paving. No interpolation or color blending used; material consistency remains pending.','Garden edge, existing tree trunk/canopy and lantern silhouette remain connected in reviewed views.'],'remainingBoundaryIssues':['West r09c05 same-coordinate paired strips need review; north/east/south neighboring tiles missing.'],'allInternalSeamsPassed':False,'allOuterTileEdgesPassed':False,'formalAccepted':False,'validation':report['validation']}
qa=R/'qa'/'east-r09c06-native-review-v01.json';assert not qa.exists();p.dump(qa,notes)
d=p.load(R/'qa'/'expansion-east-worker-map.json');art=report['outputs']['candidate'] if isinstance(report['outputs'],dict) else report['outputs'][0]
print(json.dumps({'outputsType':type(report['outputs']).__name__,'art':art}))
d.setdefault('candidateArtifacts',{})['r09_c06']={**art,'sourceIdMask':str(R/'qa'/f'{prefix}-source-id-mask.png'),'sourceReport':str(rp),'record':str(rp),'review':str(qa),'status':notes['status'],'nativeSourceCount':16,'allInternalSeamsPassed':False,'allOuterTileEdgesPassed':False,'formalAccepted':False}
d['completeCandidateTiles']=sorted(d['candidateArtifacts']);d['status']='r09_c06_complete_candidate_local_join_reselection_in_progress';d['updatedAtUtc']=p.now();d['inFlight']=False;d['unsavedSuccessfulOutput']=False
p.dump(R/'qa'/'expansion-east-worker-map.json',d)
