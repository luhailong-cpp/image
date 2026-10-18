from workflow import *
folder=ROOT/'qa/r13_c10-left-oct16-v01';j=read(folder/'seams-junctions-external.json')
issues=[
 {'id':'p22-south-independent','entries':['v22','j22'],'sources':['22v01','32v01'],'issue':'Foliage and small rock texture interrupt at horizontal y2048, particularly central stone behind foliage; south-neighbor core was unavailable when p22 guide was prepared.','repair':'22v02','status':'not_passed'},
 {'id':'p33-west-south-independent','entries':['h32','v33','j22','j32','j33'],'sources':['32v01','33v01','43v01'],'issue':'Rock facets and foliage show coordinate-aligned breaks at x2048 over row3 and y3072 over column3; now-selected neighbors can guide the native edit.','repair':'33v02','status':'not_passed'},
 {'id':'right-water-guide-material','entries':['east3','east4','v24'],'sources':['34v01','44v01'],'issue':'Visible vertical material strip at native x1024 (tile x3981) inside old selected water cores. Actual eastern joins connect, but straight guide material boundary remains.','repair':'34v02 and44v02','status':'not_passed'}]
blocked={e for i in issues for e in i['entries']}
entries=[dict(id=e['id'],file=e['file'],sha256=e['sha256'],status='reviewed_not_passed' if e['id'] in blocked else 'reviewed_no_obvious_join_defect') for e in j['entries']]
review={'createdAt':now(),'reviewer':'left_oct16','candidate':j['candidate'],'candidateSha256':j['candidateSha256'],'sourceReplayMismatchedPixels':0,'reviewedInternalSeams':24,'reviewedJunctions':9,'reviewedEastExternalSegments':4,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'overall':'fully_covered_not_passed_native_repairs_pending','issues':issues,'entries':entries,'notes':'Actual unscaled 512x1024,1024x512,512x512 contacts viewed individually. No resampling used for final. Unavailable north/west/south not claimed passed.'}
write(folder/'left-visual-review.json',review)
for f in [ROOT/'progress-left-oct16.json',ROOT/'production-resume-left-oct16-r13_c10.json']:
 p=read(f);p.update(updatedAt=now(),status=review['overall'],internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,visualReview=str(folder/'left-visual-review.json'),pendingFindings=issues);write(f,p)
print(str(folder/'left-visual-review.json'))
