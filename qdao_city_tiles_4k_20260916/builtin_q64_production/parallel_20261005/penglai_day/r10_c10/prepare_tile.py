from pathlib import Path
B=Path(__file__).resolve().parent.parent
T=B/'r10_c10'
s=(B/'r10_c11/helper.py').read_text(encoding='utf8')
s=s.replace('r10_c11','r10_c10').replace('GX,GY=40960,36864','GX,GY=36864,36864')
s=s.replace("north=Path(h['baselineCandidates'][1]['file']);east=BASE/'r10_c12/repairs/north/joint-v4/r10_c12-north-joint-candidate.png'","north=Path(h['baselineCandidates'][0]['file']);east=BASE/'r10_c11/repairs/shared-output-v7/r10_c11-candidate.png'")
s=s.replace("state={'north':", "assert p.sha(north)=='14ba18433c348ded06ff0372d56113699614621b67e1418f59ee87a89dffcc40';assert p.sha(east)=='6d78cdfd5fecc452b4cc6318863f1711c0b1420ec9f3d12c38b6aa6433c14782'\n    assert p.sha(h['plan']['file'])==h['plan']['sha256']\n    state={'north':")
s=s.replace('east repaired v4 frozen by SHA','east c11 shared-output-v7 frozen by SHA')
s=s.replace("No extra objects, denser foliage, added grooves, text", "The guide contains artificial pasted anchor bands at outer115px; reconcile their materials by drawing continuously, never reproduce the guide rectangle as a straight material cut. No extra objects, denser foliage, added grooves, text")
(T/'helper.py').write_text(s,encoding='utf8')
print(T/'helper.py')
