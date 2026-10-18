from workflow import *
q=ROOT/'qa/r13_c14-right-full-20261016-v03'
d=read(ROOT/'progress-r13_c14.json')
d.update(selectedVersions=read(ROOT/'qa/r13_c14-right-full-20261016-v03.spec.json')['patchVersions'],status='complete_native_candidate_not_passed_deferred_waterline',inFlightRequestCount=0,inFlight=[],updatedAt=now(),deferredWholeObjectIssues=[{'issue':'Small hull/foam notch at tile[1139,3072] and horizontal water cutoff in h41/v32/junction31. Waterline v01 and v02 saved but not adopted; two attempts did not remove the whole defect.','status':'deferred_after_two_unsuccessful_repair_attempts'}])
write(ROOT/'progress-r13_c14.json',d)
a=read(q/'actual-review.json');a['remainingIssue']=d['deferredWholeObjectIssues'][0]['issue'];a['inFlightRequestCount']=0;write(q/'actual-review.json',a)
write(q/'waterline-two-attempt-review.json',{'reviewedAt':now(),'originalsViewed':True,'adopted':False,'results':[{'file':str(ROOT/'native'/('r13_c14_repair_waterline_'+v+'.png')),'sha256':sha(ROOT/'native'/('r13_c14_repair_waterline_'+v+'.png')),'status':'not_passed','issue':issue} for v,issue in [('v01','Hull notch softened but water horizontal cutoff remains'),('v02','Hull/foam notch remains at local[230,627] and horizontal water cutoff persists')]],'nextAction':'Complete independent r12_c14 before concentrated deferred review'})
print('r13_c14 unchanged v03 NOTpassed, no inflight')

