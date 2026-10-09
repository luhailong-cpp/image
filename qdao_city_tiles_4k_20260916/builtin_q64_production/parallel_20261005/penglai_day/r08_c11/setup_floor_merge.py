from pathlib import Path
r=Path(__file__).resolve().parent
src=(r.parent/'r10_c14/repairs/internal/integrate_ai.py').read_text()
a=src.index('specs={');z=src.index("src=q.O/",a)
src=src[:a]+"""specs={'floor-joint':{'origin':[1421,1933],'left':[205,275],'right':[1090,1205],'top':[40,125],'bottom':[1140,1220]}}
"""+src[z:]
src=src.replace('r10_c14','r08_c11').replace("inp=q.O/(n+'-edit-input.png');gen=q.O/(n+'-ai-v1-generated.png')","inp=q.O/'references'/(n+'-input.png');gen=q.O/'native'/(n+'.png')")
src=src.replace("'method':'AI repair of stonecap, stone wall grooves and paving bevel joins, binary local masks, no image resize/blur; inherits bounded source translations from v2'","'method':'AI repair of broken paving grid near lantern, binary local masks, no image resize/blur; inherits bounded source translations from v2'")
(r/'repairs/internal/integrate_floor.py').write_text(src,encoding='utf8')

