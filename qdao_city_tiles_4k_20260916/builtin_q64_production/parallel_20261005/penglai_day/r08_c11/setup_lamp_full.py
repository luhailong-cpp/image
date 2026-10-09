from pathlib import Path
r=Path(__file__).resolve().parent
f=r/'repairs/internal/integrate_lamp.py';s=f.read_text()
s=s.replace("'top':[370,445],'bottom':[820,885]","'top':[75,115],'bottom':None")
s=s.replace('candidate-v4','candidate-v5').replace("qa(np.asarray(canvas),'v4'","qa(np.asarray(canvas),'v5'").replace('internal-v4-change-mask','internal-v5-change-mask').replace('lamp-merge-manifest.json','lamp-full-merge-manifest.json')
s=s.replace("assert np.array_equal(np.asarray(canvas)[-627:],np.asarray(Image.open(src))[-627:])","# lamp full repair ends y3699; south627 is partly changed above seam")
s=s.replace("'unchangedBands':['north627','west627','south627']","'unchangedBands':['north627','west627'],'southBandNote':'lamp ends at y3699; south shared boundary itself unaffected; joint inputs re-frozen from v5'")
s=s.replace("n+'-replacement.png'","n+'-full-replacement.png'").replace("n+'-mask.png'","n+'-full-mask.png'").replace("n+'-fields.npz'","n+'-full-fields.npz'").replace("n+'-composite.png'","n+'-full-composite.png'")
s=s.replace("['-replacement.png','-mask.png']","['-full-replacement.png','-full-mask.png']")
(r/'repairs/internal/integrate_lamp_full.py').write_text(s,encoding='utf8')
f=r/'repairs/south/helper.py';s=f.read_text().replace('internal-candidate-v4','internal-candidate-v5');f.write_text(s,encoding='utf8')

