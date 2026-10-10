#!/usr/bin/env python3
"""All-direction visual review for the low-walk candidate; no publication."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parent;out=root/'review';out.mkdir(exist_ok=True)
D=('N','NE','E','SE','S','SW','W','NW');matte=(235,232,220,255)
def board(items,cols,target,side=512):
    rows=(len(items)+cols-1)//cols;canvas=Image.new('RGBA',(cols*side,rows*(side+22)),matte);draw=ImageDraw.Draw(canvas)
    for i,(label,p) in enumerate(items):
        im=Image.open(p).convert('RGBA')
        if im.size!=(side,side):im=im.resize((side,side),Image.Resampling.LANCZOS)
        x,y=i%cols*side,i//cols*(side+22);canvas.alpha_composite(im,(x,y+22));draw.text((x+9,y+4),label,fill=(30,35,25,255))
    canvas.convert('RGB').save(target,quality=93)
for d in D:
    board([(d+' IDLE',root/'idle'/f'{d}.png')]+[(d+f'{p:02d}',root/'walk'/d/f'{p:02d}.png') for p in range(1,9)],3,out/f'{d}-idle-walk.jpg')
    paths=[root/'idle'/f'{d}.png']*4+[root/'walk'/d/f'{p:02d}.png' for p in range(1,9)]*3+[root/'idle'/f'{d}.png']*4
    seq=[]
    for p in paths:
        im=Image.new('RGBA',(512,512),matte);im.alpha_composite(Image.open(p).convert('RGBA'));seq.append(im.convert('RGB'))
    seq[0].save(out/f'{d}-idle-transition.gif',save_all=True,append_images=seq[1:],duration=100,loop=0,disposal=2)
for i,ds in enumerate((D[:4],D[4:])):
    items=[]
    for p in ('idle','01','05'):
        for d in ds:items.append((d+' '+p,root/'idle'/f'{d}.png' if p=='idle' else root/'walk'/d/f'{p}.png'))
    board(items,4,out/f'contacts-{i+1}.jpg')
board([('PORTRAIT',root/'portrait.png')]+[('IDLE '+d,root/'idle'/f'{d}.png') for d in D],3,out/'portrait-idle-eight.jpg')
seq=[]
for p in range(1,9):
    im=Image.new('RGBA',(2048,1024),matte)
    for i,d in enumerate(D):im.alpha_composite(Image.open(root/'walk'/d/f'{p:02d}.png').convert('RGBA'),(i%4*512,i//4*512))
    im=im.resize((1536,768),Image.Resampling.LANCZOS);seq.append(im.convert('RGB'))
seq[0].save(out/'eight-directions.gif',save_all=True,append_images=seq[1:],duration=100,loop=0,disposal=2)
m=json.loads((root/'manifest.json').read_text(encoding='utf-8'));q=json.loads((root/'qc.json').read_text(encoding='utf-8'))
a={'character_id':root.name,'display_name_zh':'月兔机关师','stage':'passed_numeric_qc_pending_visual_review','low_walk_edited_cells':22,'preserved_walk_cells':42,'independent_idle_frames':8,'movement_frames':64,'media_files':89,'canonical_first_contact':'RIGHT','common_scale':m['alignment']['common_scale'],'alignment_version':3,'per_subject_fit':False,'despill_policy':m['edge_despill'],'max_body_scale_cv':max(v['body_scale_cv'] for v in q['directions'].values()),'cross_direction_mean_height_ratio':q['cross_direction_mean_height_ratio'],'max_idle_walk_height_drift':max(v['idle_walk_height_drift'] for v in q['directions'].values()),'max_head_axis_deviation_px':max(v['horizontal_body_axis_max_deviation_px'] for v in q['directions'].values()),'status':'pending_root_visual_review_not_publish','sealed':False,'published':False}
(root/'processing/candidate-audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(a,ensure_ascii=False))
