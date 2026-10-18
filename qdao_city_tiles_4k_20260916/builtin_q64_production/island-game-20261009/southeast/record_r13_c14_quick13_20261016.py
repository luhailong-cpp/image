from workflow import ROOT,read,write,sha,now
from pathlib import Path
d=read(ROOT/'progress-r13_c14.json')
review={'atUtc':now(),'tile':'r13_c14','stage':'quick layout and neighbor join review, not full-tile acceptance','entries':[]}
for rc,ver,notes in [('12','v01','Layout and W actual seam PASS; spar aligns.'),('21','v01','Layout and W/N contour continuity PASS; mast material horizontal guide edge needs whole-object repair, tile remains NOTpassed.'),('31','v01','W/N/S structural joins PASS; lower hull straight material step spans planks, defer localized repair after full assembly.'),('42','v02','Boat lower-left fragment correct; W/E/S water and hull joins PASS.'),('24','v01','Water-only layout and S join PASS.'),('33','v01','Water-only layout and E/S joins PASS.'),('22','v01','Post exact layout, N/W post and gunwale continuity PASS.'),('14','v01','Water-only layout and S continuity PASS.')]:
 p=ROOT/'native'/f'r13_c14_p{rc}_{ver}.png';d['selectedVersions'][rc]=ver
 review['entries'].append({'file':str(p),'sha256':sha(p),'note':notes,'wholeTileAccepted':False})
d.update({'generatedNativeCount':len(list((ROOT/'native').glob('r13_c14_p*.png'))),'usableNativeCount':len(d['selectedVersions']),'updatedAt':now(),'missingPatchCoordinates':[f'{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in d['selectedVersions']],'inFlightRequestCount':2,'inFlight':['r13_c14_p23_v01','r13_c14_p32_v01'],'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'deferredWholeObjectIssues':[{'patch':'21','issue':'mast horizontal material division at native y230','status':'pending_first_repair_after_assembly'},{'patch':'31','issue':'lower hull color step crossing several planks near native x717','status':'pending_first_repair_after_assembly'}]})
write(ROOT/'qa/right-current-20261013/r13_c14-quick-review-20261016-13.json',review);write(ROOT/'progress-r13_c14.json',d)

