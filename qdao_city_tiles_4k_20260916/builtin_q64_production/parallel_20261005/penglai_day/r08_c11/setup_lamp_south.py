from pathlib import Path
r=Path(__file__).resolve().parent;f=r/'repairs/internal/integrate_floor.py';s=f.read_text()
s=s.replace("'floor-joint':{'origin':[1421,1933],'left':[205,275],'right':[1090,1205],'top':[40,125],'bottom':[1140,1220]}","'lamp-join':{'origin':[850,2445],'left':[160,210],'right':[800,900],'top':[370,445],'bottom':[820,885]}")
s=s.replace('candidate-v3','candidate-v4').replace('candidate-v2','candidate-v3').replace("qa(np.asarray(canvas),'v3'","qa(np.asarray(canvas),'v4'").replace('internal-v3-change-mask','internal-v4-change-mask').replace('ai-merge-manifest.json','lamp-merge-manifest.json')
(r/'repairs/internal/integrate_lamp.py').write_text(s,encoding='utf8')
old=r.parent/'r08_c12/repairs/south'
for n in ['helper.py','quilt.py']:
 s=(old/n).read_text().replace('r08_c12','r08_c11').replace('r09_c12','r09_c11').replace('45056','40960').replace('region-v3','region-v6').replace('3f6cb3390620292ed2c4495cccf7b454428df1bedcb09d2eb41dd5b85cb0b226','149ca13e45f84edb2b69e1a637b56e765af821d209e11e953708a9d05ce5fc8f').replace('internal-candidate-v2','internal-candidate-v4')
 d=r/'repairs/south'/n;d.parent.mkdir(exist_ok=True);assert not d.exists();d.write_text(s,encoding='utf8')

