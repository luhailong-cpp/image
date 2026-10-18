from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,datetime
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
i=json.loads((Q/'inputs-v1.json').read_text());n=i['northSource'];s=i['southSource']
assert sha(n['path'])==n['sha256'];assert sha(s['path'])==s['sha256']
ni=Image.open(n['path']);si=Image.open(s['path'])
findings=[];checks=[]
descs=[
'Visible straight horizontal cyan/value step across the whole segment at the actual core join. The north texture is noticeably softer and the south texture sharper; ripple contours are abruptly clipped at y230 in the evidence crop.',
'Strong horizontal texture and value discontinuity at the actual core join; the large softer northern ripples change to smaller sharper southern facets along a straight line. Several white ripple paths terminate or change thickness at the join.',
'Horizontal cyan/value step persists through water and the white-foam setting. The large blue pool near segment center has an abrupt value/texture change along the actual core boundary; this is visible even though broad foam placement is similar.',
'Horizontal cyan/value and ripple-detail discontinuity remains across the foamy water below the rock. The upper rock itself is outside the seam, but the foam/water transition is visibly cut on the core boundary.'
]
for c,desc in zip(i['crops'],descs):
    a=np.asarray(Image.open(c['path']));assert sha(c['path'])==c['sha256']
    assert np.array_equal(a[:230],np.asarray(ni.crop(c['northSourceContextBox'])))
    assert np.array_equal(a[230:],np.asarray(si.crop(c['southSourceContextBox'])))
    checks.append({**c,'viewed':True,'viewDetail':'original','visualStatus':'failed-external-seam','cropPixelIdentity':True})
    x0=c['northSourceContextBox'][0];x1=x0+1024;gx=20365+x0
    findings.append({'id':f"N{c['segment']:02d}",'status':'unresolved','severity':'visible-seam','segment':c['segment'],'description':desc,'seamGlobalY':49152,'globalBox':[gx,49122,gx+1024,49182],'northContextBox':[x0,4181,x1,4211],'southContextBox':[x0,115,x1,145],'evidence':{'path':c['path'],'sha256':c['sha256'],'imageBox':[0,200,1024,260],'seamImageY':230},'suggestedNextScope':'Native seam repair using frozen r12 actual core as north anchor, then inspect repaired center and all selection boundaries; no repair performed by this review.'})
rec={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'/root/resume_r12c06_oct16','status':'failed-r13c06-north-external-actual-core-join','formalAccepted':False,'northSource':n,'southSource':s,'seamGlobalY':49152,'reviewedGlobalStrip':[20480,48922,24576,49382],'method':'Four 1024x460 original-scale evidence crops. Each uses r12 actual core context rows3981..4211 above r13 actual core rows115..345. Both source halves verified pixel-identical. All four images actually viewed at original detail. No halo pixels substituted for core.','nativeCropsActuallyViewed':4,'checks':checks,'findings':findings,'relationshipToUpperHaloFinding':'UH01 from prior W08 upper review was confined to north halo. The four N findings here concern the real r12/r13 core-to-core join and supersede any assumption that north-halo appearance establishes exterior continuity.','scopeNote':'This report does not invalidate passed internal scope checks whose source pixels are unchanged; it leaves the north external seam unpassed. No source artwork was changed.','otherExternalEdges':'not reviewed here','artworkMutated':False,'aiGenerationUsed':False,'gitOperations':False,'proof':{'sourceHashUnchanged':True,'northPixelIdentityMismatches':0,'southPixelIdentityMismatches':0,'cropHashMismatches':0}}
with (Q/'review-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(Q/'review-v1.json'),'sha256':sha(Q/'review-v1.json'),'status':rec['status'],'findings':len(findings)},ensure_ascii=False))
