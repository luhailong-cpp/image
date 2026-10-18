import sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
from pathlib import Path
q=w.Z/'qa/r07_c11-west-resume-v1';m=w.read(q/'manifest.json');reuse=w.read(q/'quick-review-reuse-proof.json');proof={Path(e['file']).name:e for e in reuse['checks']}
failed={'core_p34.native-1to1.png':'Known blue bollard right boundary disagreement near local x900..1170,y1030..1139; join to independent p44 unresolved','core_p42.native-1to1.png':'Artificial straight stone-to-wood internal boundary x1024,y115..460','h_p34_p44.native-1to1.png':'Blue bollard upper cap/stave discontinuity at row3/4 join; left rail section now continuous','h_p32_p42.native-1to1.png':'Stone-to-wood boundary becomes an artificial straight vertical segment below row3/4 join','v_p42_p43.native-1to1.png':'True x128 core seam continuous, but view includes artificial stone/wood line at x13 on its left edge','junction_r3_c2.native-1to1.png':'Same p42 artificial stone/wood line visible left of true junction'}
checks=[]
for e in m['qa']:
 name=Path(e['file']).name;kind=e['kind'];x=dict(file=e['file'],sha256=e['sha256'],kind=kind,visualPassed=name not in failed,formalAccepted=False)
 if kind=='four_patch_junction':x['method']='Direct native1to1 512px view in current review';x['note']=failed.get(name,'All four source contours and material transitions continuous at junction')
 elif kind=='whole_core':
  pid='r07_c11_'+name.split('.')[0].removeprefix('core_');src=Path(w.own_selection('r07_c11')[pid]['path']);stem=src.stem.removesuffix('-west_sol');rp=w.R/(stem+'.review.json');assert rp.exists();x.update(method='Reuse full1254 native visual inspection for identical generated source; exact core pixel equality proved by manifest',source=w.ref(src),reviewRecord=w.ref(rp),note=failed.get(name,'Original native fully viewed and locally reviewed; exact crop unchanged'))
 else:
  pr=proof[name];assert pr['exactPixelSubsetVerified'];x.update(method='Reuse directly inspected native quick strip, exact byte-equal RGB subset verified',quickView=pr['reusedQuickView'],note=failed.get(name,'Core seam and visible contours continuous'))
 checks.append(x)
assert len(checks)==49
out=dict(schemaVersion=1,reviewer='roof_resume',reviewedAtUtc=w.now(),candidate=m['candidate'],selection=m['selection'],manifest=w.ref(q/'manifest.json'),reuseProof=w.ref(q/'quick-review-reuse-proof.json'),checks=checks,checkedCount=49,passCount=sum(x['visualPassed'] for x in checks),pendingCount=sum(not x['visualPassed'] for x in checks),internalVisualPassed=False,independentAccepted=False,formalAccepted=False,status='candidate_16_cores_two_issue_groups_pending',issueGroups=[dict(id='bollard-joint',worldBox=[44817,27635,45056,27776],description='p34/p44 cap and blue stave contour mismatch; p44 stable right neighbor valid; fix north to stable new lower geometry'),dict(id='p42-material-edge',worldBox=[42875,27648,42910,28000],description='Artificial straight vertical stone/wood boundary in p42; left edge used for p41 is independent and clean')])
w.write(q/'roof-resume-review-v1.json',out)
print(dict(checked=49,passed=out['passCount'],pending=out['pendingCount'],review=str(q/'roof-resume-review-v1.json')))

