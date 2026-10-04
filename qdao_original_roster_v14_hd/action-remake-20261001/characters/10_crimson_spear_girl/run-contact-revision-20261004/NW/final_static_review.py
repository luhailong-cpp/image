from pathlib import Path
from PIL import Image
import json,hashlib,datetime
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
for d in ('W','NW'):
    folder=root/'run-contact-revision-20261004'/d
    selected=json.loads((folder/'selection.json').read_text())['slots']
    selected_names={Path(p).name for p in selected.values()}
    rows=[]
    for n in range(1,17):
        slot=f'run/{d}/{n:02d}'; p=root/selected.get(slot,f'runtime/{slot}.png')
        im=Image.open(p).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        a=im.getchannel('A'); bbox=a.point(lambda v:255 if v>=32 else 0).getbbox()
        phase=(n-5)%16; foot='LEFT' if phase<8 else 'RIGHT'; phase=phase%8; zone=phase//2+1
        rows.append({'frame':n,'supportFoot':foot,'spatialPositionPair':zone,'pairPose':phase%2+1,'source':str(p.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':Image.open(p).size,'alpha32BBoxAt1024':bbox,'edgeTouch':bool(bbox and (bbox[0]==0 or bbox[1]==0 or bbox[2]==1024 or bbox[3]==1024)),'staticReview':'Visible aligned fullsole or forefoot support; other foot raised. Pair progression manually reviewed in selected-feet-review.jpg.'})
    audit={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':d,'status':'static-pose-review-passed; parent-integrated-playback-review-required','timing':{'frames':16,'frameMs':75,'totalMs':1200,'repeats':False},'supportSequence':{'LEFT':[[5,6],[7,8],[9,10],[11,12]],'RIGHT':[[13,14],[15,16],[1,2],[3,4]]},'frames':rows,'sourceUnique':len({x['sha256'] for x in rows})==16,'noAlpha32EdgeContact':not any(x['edgeTouch'] for x in rows),'remainingItems':['Parent must inspect integrated 75ms playback, including body/weapon bob and loop transition.'],'modelDisclosure':'Builtin host-managed; actual model and quality not disclosed, left null; configuration snapshot retained.'}
    (folder/'final-static-review.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf8')
    for record in folder.glob('*.native.png.generation.json'):
        data=json.loads(record.read_text(encoding='utf8')); fn=record.name.removesuffix('.generation.json')
        data['status']='selected-after-static-review' if fn in selected_names else 'rejected-not-selected'
        if fn not in selected_names:
            data['rejectionReason']='Not selected after posture/framing review; generated alternatives retain provenance only until final production cleanup.'
        else:
            data['reviewEvidence']='selected-feet-review.jpg and final-static-review.json'
        for idx,ref in enumerate(data.get('references',[])):
            src=Path(ref['file']); srcrec=Path(str(src)+'.generation.json')
            if srcrec.exists():
                snapshot=folder/(record.name+'.input-'+str(idx+1)+'.json')
                if not snapshot.exists(): snapshot.write_bytes(srcrec.read_bytes())
                ref['generationRecordSnapshot']=snapshot.name
        record.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
    print(d, 'static frames',len(rows),'unique',audit['sourceUnique'],'edges clear',audit['noAlpha32EdgeContact'])

