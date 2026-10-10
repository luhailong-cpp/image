#!/usr/bin/env python3
"""Reproduce low-walk candidate; no seal or publish. Verify despill alpha invariants."""
from pathlib import Path
import subprocess,sys,json,hashlib
from PIL import Image
root=Path(__file__).resolve().parent;base=root.parent.parent;source=root/'source';review=base/'review/28_low_walk_fixes'
def pix(path):return hashlib.sha256(Image.open(path).convert('RGBA').tobytes()).hexdigest()
changes={(r['direction'],r['canonical_phase']) for r in json.loads((review/'selected-all-22.json').read_text(encoding='utf-8'))}
baseline=json.loads((review/'baseline/manifest.json').read_text(encoding='utf-8'))
protected={}
for record in baseline['files']:
    relative=record['path'];parts=relative.split('/')
    keep=relative=='portrait.png' or (len(parts)==2 and parts[0]=='idle') or (len(parts)==3 and parts[0]=='walk' and parts[2][:2].isdigit() and (parts[1],int(parts[2][:2])) not in changes)
    if keep:protected[relative]=record['sha256']
assert len(protected)==51
resume='--resume-despill' in sys.argv
if not resume:subprocess.run([sys.executable,'-X','utf8','-B',str(source/'assemble_28_low_walk_candidate.py')],check=True)
command=[sys.executable,'-X','utf8','-B',str(base/'process_roster.py'),'--character-dir',str(root)]
for flag,name in [('--s-e','s_e'),('--n-w','n_w'),('--ne-sw','ne_sw'),('--nw-se','nw_se'),('--idle','idle')]:command.extend([flag,str(source/(name+'.png'))])
command.extend(['--portrait-raw',str(source/'portrait-daoist.png'),'--alignment-version','3','--common-scale','1.02941176470588'])
# Establish the actual new-pose alpha/geometry, then verify color-only despill does not alter it.
if not resume:subprocess.run(command,check=True)
before={}
frame_paths=[root/'idle'/f'{d}.png' for d in ['N','NE','E','SE','S','SW','W','NW']]+[root/'walk'/d/f'{p:02d}.png' for d in ['N','NE','E','SE','S','SW','W','NW'] for p in range(1,9)]
for p in frame_paths:
    im=Image.open(p).convert('RGBA');relative=p.relative_to(root).as_posix();before[relative]={'alpha_sha256':hashlib.sha256(im.getchannel('A').tobytes()).hexdigest(),'green_sha256':hashlib.sha256(im.getchannel('G').tobytes()).hexdigest(),'alpha_bbox':list(im.getchannel('A').getbbox())}
assert len(before)==72
(root/'processing/before-despill-invariants.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
subprocess.run(command+['--despill-magenta-edge','--despill-radius','4'],check=True)
for relative,record in before.items():
    im=Image.open(root/relative).convert('RGBA')
    assert hashlib.sha256(im.getchannel('A').tobytes()).hexdigest()==record['alpha_sha256'],relative
    assert hashlib.sha256(im.getchannel('G').tobytes()).hexdigest()==record['green_sha256'],relative
    assert list(im.getchannel('A').getbbox())==record['alpha_bbox'],relative
for relative,digest in protected.items():assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest,'Unexpected changed preserved output '+relative
(review/'export-preservation-checks.json').write_text(json.dumps({'status':'passed','preserved_output_png_byte_exact':len(protected),'preserved_walk':42,'preserved_idle':8,'preserved_portrait':1,'despill_alpha_green_bbox_exact_frames':len(before),'common_scale':1.02941176470588,'alignment_version':3,'despill_radius':4,'sealed':False,'published':False},indent=2)+'\n',encoding='utf-8')
result=subprocess.run([sys.executable,'-X','utf8','-B',str(base/'verify_delivery.py'),'--character-dir',str(root),'--allow-pending-visual'],check=True,capture_output=True,text=True,encoding='utf-8')
(root/'verification-pending.log').write_text(result.stdout,encoding='utf-8');print(result.stdout)
print('Verified unchanged42walk+8idle+portrait and color-only despill invariants for72 frames')
