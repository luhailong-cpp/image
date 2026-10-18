from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import production as p
q=p.ROOT/'qa'; prefix='west-r09c02-bamboo-upper-v02'
d=p.load(q/'expansion-west-worker-map.json'); m=p.load(q/(prefix+'-manifest.json')); t=m['tiles'][0]
old=d['candidateArtifacts']['r09_c02']
new={**old,'path':t['candidate']['path'],'sha256':t['candidate']['sha256'],'sourceReport':t['report']['path'],'record':t['report']['path'],'sourceIdMask':t['sourceIdMask'],'review':str(q/(prefix+'-review.json')),'internalStatus':'needs_local_repairs','internalTileSeamsPassed':False,'formalAccepted':False,'nativePixelsVerified':True,'supersedesCandidate':{'path':old['path'],'sha256':old['sha256']}}
d['candidateArtifacts']['r09_c02']=new
d['updatedAtUtc']=p.now(); d['currentRequest']='r09_c01_s03_04_v01';p.dump(q/'expansion-west-worker-map.json',d)
print(new['path'])
