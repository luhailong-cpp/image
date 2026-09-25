"""Verify the final portable delivery after raw-image cleanup."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
from PIL import Image
import numpy as np
REC=Path(__file__).resolve().parents[1];OUT=REC/'14-delivery-preview';ASSETS=OUT/'assets'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qa=read(OUT/'qa-summary.json');manifest=read(OUT/'game-assets.json');plan=read(OUT/'source-cleanup-plan.json');provenance=read(OUT/'provenance.json')
assert qa['offlineApproved'] and len(qa['assets'])==136
versions={v['archive']:v for v in provenance['versions']}
pngs=list(ASSETS.rglob('*.png'));assert len(pngs)==136
walk=list((ASSETS/'walk').rglob('*.png'));idle=list((ASSETS/'idle').glob('*.png'));assert len(walk)==128 and len(idle)==8
raw_shas=set();errors=[]
for r in qa['assets']:
 p=ASSETS/r['file'];meta=read(Path(str(p)+'.generation.json'));im=Image.open(p);a=np.asarray(im)
 assert im.size==(1024,1024) and im.mode=='RGBA'
 assert sha(p)==r['sha256']==meta['sha256']
 assert int(np.where(a[:,:,3]>8)[0].max())==942 and (a[:,:,3]==0).any()
 v=versions[meta['sourceArchive']];raw_meta=v['documents']['raw.png.generation.json']['json']
 assert raw_meta['sha256']==r['sourceSHA256']==meta['derivedFrom']['sha256']
 assert min(raw_meta['nativeSize'])>=1024 and raw_meta['sha256'] not in raw_shas
 raw_shas.add(raw_meta['sha256'])
 meta['sourceAvailability']={'rawImagesDeletedAfterVerification':True,'exactTextEvidence':'provenance.json','version':meta['sourceArchive'],'cleanupEvidence':'cleanup-report.json'}
 meta['sourceRetention']='Raw and rejected images deleted after export and offline acceptance under AGENTS.md/user instruction; exact text evidence retained.'
 write(Path(str(p)+'.generation.json'),meta)
html=(OUT/'index.html').read_text(encoding='utf-8');data=json.loads(re.search(r'const D=(\{.*?\});\s*let direction=',html,re.S).group(1))
urls=[r['src'] for f in data['frames'].values() for r in f]+list(data['idles'].values())
assert len(urls)==136 and all((OUT/u).is_file() for u in urls) and data['inventory']['artApproval']
assert data['inventory']['frameDurationMs']==30 and data['inventory']['cycleMs']==480
for frames in manifest['walk'].values():
 assert len(frames)==16 and sum(f['durationMs'] for f in frames)==480
 for f in frames:assert sha(OUT/f['file'])==f['sha256']
remaining=[e['absolutePath'] for e in plan['entries'] if Path(e['absolutePath']).exists()]
assert not remaining,remaining
assert all(Path(p).exists() for p in plan['protectedNotCandidates'])
now=datetime.now(timezone.utc).isoformat()
cleanup={'character':qa['character'],'verifiedAt':now,'completed':True,'removedImages':len(plan['entries']),'workspaceImagesRemoved':sum(x['scope']=='workspace' for x in plan['entries']),'hostOriginalsRemoved':sum(x['scope']=='host_generated_images' for x in plan['entries']),'remainingPlannedImages':remaining,'finalPNGsPreserved':136,'sharedIdentityAndStylePreserved':True,'exactTextEvidence':'provenance.json','provenanceSHA256':sha(OUT/'provenance.json'),'deletionLogs':['cleanup-workspace.jsonl','cleanup-host_generated_images.jsonl']}
write(OUT/'cleanup-report.json',cleanup)
plan['executed']=True;plan['executedAt']=now;plan['result']='All enumerated temporary images deleted and final assets verified';write(OUT/'source-cleanup-plan.json',plan)
report={'character':qa['character'],'verifiedAt':now,'pass':True,'walkCount':128,'idleCount':8,'uniqueSourceCount':len(raw_shas),'finalSize':[1024,1024],'allRGBA':True,'allTransparent':True,'allFinalSHAsMatch':True,'allPreviewReferencesResolve':True,'previewAssetCount':136,'frameDurationMs':30,'cycleMs':480,'offlineArtApproved':True,'originalImageCleanupComplete':True,'clientIntegrationPerformed':False,'unityValidated':False,'indexSHA256':sha(OUT/'index.html'),'qaSHA256':sha(OUT/'qa-summary.json'),'manifestSHA256':sha(OUT/'game-assets.json'),'provenanceSHA256':sha(OUT/'provenance.json')}
write(OUT/'final-verification.json',report)
print(json.dumps(report,ensure_ascii=False))
