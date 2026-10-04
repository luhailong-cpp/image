from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
f=root/'run-contact-revision-20261004/N'
p=f/'selection.json'; data=json.loads(p.read_text(encoding='utf8'))
updates={6:'06-position4-v2',7:'07-position4-v2',14:'14-position4-v4',15:'15-position4-v5'}
previous={n:data['slots'][f'run/N/{n:02d}'] for n in updates}
for n,folder in updates.items():data['slots'][f'run/N/{n:02d}']=f'run-contact-revision-20261004/N/{folder}/native.png'
data['status']='four-rearmost-support-slots-revised-after-independent-review; other slots unchanged'
p.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
sheet=Image.new('RGB',(1280,1024),(232,232,224));draw=ImageDraw.Draw(sheet);rows=[]
for k,(n,folder) in enumerate(updates.items()):
    row={'frame':n,'previousSource':previous[n],'newSource':data['slots'][f'run/N/{n:02d}'],'measurements':{}}
    for col,src in enumerate((root/previous[n],f/folder/'native.png')):
        im=Image.open(src).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        crop=im.crop((335,660,665,1005)).resize((300,315),Image.Resampling.LANCZOS)
        x=k*320; y=col*500
        draw.text((x+5,y+6),f'N {n:02d} '+('before' if col==0 else 'after'),fill=(20,20,20))
        sheet.paste(crop,(x,y+38),crop)
        a=im.getchannel('A').point(lambda v:255 if v>=32 else 0);bbox=a.getbbox()
        foot=a.crop((400 if n<8 else 510,820,520 if n<8 else 660,1024)).getbbox()
        head=a.crop((345,150,680,450)).getbbox()
        row['measurements']['before' if col==0 else 'after']={'alpha32BBoxAt1024':bbox,'supportFootLowestY':820+foot[3]-1 if foot else None,'headTopY':150+head[1] if head else None,'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest()}
    rows.append(row)
    gen=f/folder/'native.png.generation.json'; meta=json.loads(gen.read_text(encoding='utf8'));meta['status']='selected-after-visual-review';meta['reviewEvidence']='run-contact-revision-20261004/N/rearmost-four-review.json';gen.write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf8')
out=f/'rearmost-four-before-after.jpg';sheet.save(out,quality=95)
audit={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':[6,7,14,15],'selectionUpdated':True,'rows':rows,'spatialPlanConfirmed':{'LEFT':[[16,1],[2,3],[4,5],[6,7]],'RIGHT':[[8,9],[10,11],[12,13],[14,15]]},'visualReview':'Four new independent poses retain upper-body framing and complete two-handed spear. N06/07 rearward contact extended relative to pelvis; N14/15 no longer retract toward prior third spatial position and boot gemstones restored red, head/waist gems remain turquoise. No visible outward ankle yaw. Fullcanvas output only, no sprite translation or duplicated frame. Ground-plane contact assessed visually, lowest-pixel measurements are ancillary not a grounding transform.','remaining':'Parent integrated 75ms playback review.'}
(f/'rearmost-four-review.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf8')
(f/'rearmost-four-before-after.jpg.generation.json').write_text(json.dumps({'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':[{'file':x['previousSource'],'sha256':x['measurements']['before']['sourceSHA256']} for x in rows]+[{'file':x['newSource'],'sha256':x['measurements']['after']['sourceSHA256']} for x in rows],'operation':'Review-only uniform1024 then constant crop montage; no pixel edits to sprite'},indent=2),encoding='utf8')
print(json.dumps(rows,indent=2))

