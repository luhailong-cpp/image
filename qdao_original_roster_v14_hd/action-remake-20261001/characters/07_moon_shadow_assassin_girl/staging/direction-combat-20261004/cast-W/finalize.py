from pathlib import Path
import json,hashlib
from PIL import Image
P=Path(__file__).parent
R=P.parents[2]
rows=[]
for n in range(1,17):
    p=P/(f'{n:02}-v3.png' if n==10 else f'{n:02}-v1.png'); r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.size==(1254,1254)
        a=im.getchannel('A'); edge=max(a.crop(b).getextrema()[1] for b in [(0,0,1254,1),(0,1253,1254,1254),(0,0,1,1254),(1253,0,1254,1254)])
        assert edge<=8
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    rows.append({'id':f'cast_W_{n:02}','action':'cast','direction':'W','frame':n,'selected':str(p),'sha256':r['sha256'],'generationRecord':str(p)+'.generation.json','staticReviewed':True,'notes':r['visualReview']['notes'],'edgeMaxAlpha':edge,'durationMs':45})
doc={'schemaVersion':1,'reviewer':'/root/direction_south_recheck','status':'15_selected_W10_pending_root_retry','selected':rows,'staticReviewed':True,'scope':'15 cast/W frames selected; W10 excluded because both candidates failed edge constraints','preserved':'front foot, knee and ankle positions, sole pitch, pose, hands, two daggers, framing','modelEvidence':'config target Sunburst/max; builtin actual model and quality null','rejected':[{'id':'cast_W_10','candidate':'10-v1.png','edgeMaxAlpha':55,'reason':'edge >8'},{'id':'cast_W_10','candidate':'10-v2.png','edgeMaxAlpha':167,'reason':'edge >8; builtin retry failed edge cleanup'}]}
doc['status']='16_selected_native_pending_root_publish'
doc['scope']='16 cast/W frames selected; W10-v3 edge repair replaces rejected v1 and v2'
(R/'review/direction-combat-20261004/selection-cast-west.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'selection.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
print('16 native cast/W candidates validated and selection-cast-west.json saved.')
