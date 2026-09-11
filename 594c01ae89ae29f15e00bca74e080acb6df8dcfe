
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
p=Path(r'E:/work/image/qdao_chibi_roster_v11/26_osmanthus_healer')
ds=['S','SW','W','NW','N','NE','E','SE']
checks={'portrait_size':list(Image.open(p/'portrait.png').size),'portrait_mode':Image.open(p/'portrait.png').mode,'frame_count':0,'directions':{}}
assert checks['portrait_size']==[1024,1024] and checks['portrait_mode']=='RGBA'
for d in ds:
    fr=[p/'walk'/d/f'{i:02d}.png' for i in range(1,5)]
    hs=[]
    for f in fr:
        im=Image.open(f);assert im.size==(512,512) and im.mode=='RGBA'
        assert im.getchannel('A').getextrema()[0]==0
        hs.append(hashlib.sha256(im.tobytes()).hexdigest())
    assert len(set(hs))==4
    strip=Image.open(p/'walk'/d/'strip.png');assert strip.size==(2048,512) and strip.mode=='RGBA'
    gif=Image.open(p/'walk'/d/'walk.gif');assert gif.n_frames==4
    durations=[]
    for i in range(4):
        gif.seek(i);durations.append(gif.info.get('duration'));assert gif.info.get('duration')==120
    checks['frame_count']+=4;checks['directions'][d]={'frames':4,'unique_frames':4,'strip_size':[2048,512],'gif_frames':4,'gif_durations_ms':durations}
q=json.loads((p/'qc.json').read_text(encoding='utf8'))
assert not q['errors']
q['status']='passed'
q['visual_review']={'status':'passed','reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex visual inspection','character_identity':'consistent chibi elderly herbal healer: plump mature face, bamboo hat, osmanthus bun ornament, indigo ivory robe, herb basket and jade taiji waist clasp','direction':'All eight direction rows visually reviewed. SW was redrawn as front-left with both eyes visible to distinguish it from W. E has a separate right-facing source; prior front-right drawing was reclassified as SE.','gait':'Visible individual foot positions, lifted stepping feet and arm swings across four independently generated images per direction. Small hand-painted costume and gait differences retained.','silhouette':'Hat, basket, fingers and shoes complete; transparent edges and fixed feet baseline inspected.','limitations':'Four-frame hand-painted short walk loops; no skeleton, runtime locomotion or engine validation included.'}
q['artifact_checks']=checks
(p/'qc.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(p/'processing/export-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(p/'sources/SW-correction.txt').write_text('Final walk_SW_2x2.png was generated with built-in image_gen from a visible crop of the S reference and an explicit front-left orientation. The original wrong right-facing SW drawing is retained as rejected_SW_facing_right.png; the first left-facing near-profile refinement is retained as alternate_SW_near_profile.png. No mirroring or pose synthesis was used. Final native source is 1254x1254.\n',encoding='utf8')
m=json.loads((p/'manifest.json').read_text(encoding='utf8'))
m['display_name']='桂香药婆';m['direction_correction']='sources/SW-correction.txt';m['qc_status']='passed'
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'character':p.name,'status':'passed','frames':checks['frame_count'],'strips':8,'gifs':8,'cross_direction_height_ratio':q['cross_direction_mean_height_ratio'],'max_body_scale_cv':max(v['body_scale_cv'] for v in q['directions'].values()),'foot_y_std_max':max(v['output_foot_y_std'] for v in q['directions'].values())},ensure_ascii=False))

