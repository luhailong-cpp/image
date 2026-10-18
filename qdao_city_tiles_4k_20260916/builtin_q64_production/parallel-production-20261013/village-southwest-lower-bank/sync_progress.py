from produce import *
records=[json.loads(p.read_text()) for p in (ROOT/'native').glob('*.generation.json')]
selected=[r for r in records if r.get('selected')]
keys={(r['tile'],r['patch']) for r in selected}
assert len(keys)==len(selected), 'duplicate selected core'
for r in selected:
    assert sha(r['file'])==r['sha256']
    assert Image.open(r['file']).size==(1254,1254)
counts={t:sum(k[0]==t for k in keys) for t in ['r12_c03','r12_c04']}
write(ROOT/'selected-sources.json',{'sources':[{'tile':r['tile'],'patch':r['patch'],'file':r['file'],'sha256':r['sha256']} for r in selected],'uniqueSelectedCores':len(keys),'generatedVersions':len(records)})
write(ROOT/'progress.json',{'status':'full_coverage_native_seam_repair_pending','selectedCores':len(keys),'uniqueSelectedCores':len(keys),'generatedVersions':len(records),'targetCores':32,'tileCoreCounts':counts,'fullCoverage4kCount':sum(v==16 for v in counts.values()),'complete4kCount':0,'internalPassed4kCount':0,'rejectedOrSupersededVersions':len(records)-len(keys),'actualModel':None,'updatedAtUtc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'uniqueSelectedCores':len(keys),'generatedVersions':len(records),'tileCoreCounts':counts}))
