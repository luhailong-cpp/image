from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/north-corner3072-20261016')
Q=T/'qa/native-23-source-incremental-20261016T070108286530Z-20aa64f66666c666'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(D/'adoption-proposal-fix02.json');out=Q/'north-corner-fix02-independent-local-review.json';assert not out.exists()
write(out,{'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'passed_local_native_adoption','proposal':ref(D/'adoption-proposal-fix02.json'),'sourceSha256':p['sourceSha256'],'maskSha256':p['maskSha256'],'pixelCount':p['selectedPixelCount'],'rootReview':ref(D/'root-local-review-fix02.json'),'crops':[dict(ref(D/('fix02-'+n+'.png')),actuallyViewed=True,status='passed_local_geometry_and_perimeter') for n in ['detail','north','south','west','east']],'finding':'Viewed complete repair detail and all four native perimeters. Continuous physical beveled curb closes the prior rectangular notch; neighboring grout and ivory trim remain connected. Residual fine stone-tone variation at the fixed northern row boundary does not present a structural cut or broad horizontal light/dark strip in the reviewed fix02 crop. Only fix02 ROI entirely within current tile is approved. Fixed north neighbor pixels remain untouched.','rejectedEarlierProposals':['adoption-proposal.json','adoption-proposal-v2.json'],'fullTileInternalQAPassed':False,'formalAccepted':False})
prompt=Q/'north-corner-fix02-exact-prompt.txt';assert not prompt.exists()
prompt.write_text(read(D/'request-fix02.json')['parameters']['prompt'],encoding='utf-8')
cfg={'baseManifest':str(Q/'full-audit-reviewed-status.json'),'patches':[{'proposal':str(D/'adoption-proposal-fix02.json'),'independentReview':str(out),'generationRecord':str(D/'generation-fix02.json'),'request':str(D/'request-fix02.json'),'prompt':str(prompt),'receipt':str(D/'tool-receipt-fix02.json')}]}
dest=T/'increment-24-source-config-20261016.json';assert not dest.exists();write(dest,cfg)
print(str(dest))

