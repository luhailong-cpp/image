from native_work import *
name='r06_c12-continued-v1-20261016'
tile=ZONE/'tiles'/f'{name}.png'
files=[ZONE/'qa'/f'{name}-final'/f'{x}-100pct.png' for x in ['cross-3-2','cross-3-3','vertical-3-segment-4']]
out=ZONE/'qa'/f'{name}-root-independent-spotreview-20261016.json'
assert not out.exists()
write(out,{'tileId':'r06_c12','candidatePath':tile.as_posix(),'candidateSha256':sha(tile),'reviewedAtUtc':now(),'reviewer':'root','scope':'Independent preview and3 critical100pct crops; full49 prior worker QA retained','status':'passed_spot_review_only','observations':['Gold-red ridge, blue tile outlines and background leaf branches remain continuous at reviewed bottom-row intersections.','Preview inspected for broad daylight courtyard, trees and cropped roof layout; preview is not native detail evidence.'],'crops':[{'file':p.as_posix(),'sha256':sha(p),'status':'passed_direct_visual100pct'} for p in files],'formalAccepted':False})
print(out.as_posix())

