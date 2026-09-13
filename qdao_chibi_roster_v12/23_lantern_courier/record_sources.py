from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for direction,index in [('NE',1),('E',2),('SE',3),('SW',5),('W',6),('NW',7)]:
 raw=root/f'source/walk-{direction}-original.png'
 if not raw.exists():raw=root/f'source/walk-{direction}.png'
 prompt=root/f'prompts/walk-{direction}.txt';guide=root/f'references/pose-{direction}.png'
 if not raw.exists() or not prompt.exists():continue
 obj={'source':'Built-in image_gen; new character redraw using two visual references','direction':direction,'grid':[4,2],'raw_native_size':list(Image.open(raw).size),'raw_path':str(raw.relative_to(root)),'raw_sha256':sha(raw),'identity_reference':{'path':'source/idle.png','sha256':sha(root/'source/idle.png'),'view_index':index},'pose_reference':{'path':str(guide.relative_to(root)),'sha256':sha(guide),'phase_order_from_approved_Han':[5,6,7,8,1,2,3,4],'reference_only_not_final_artwork':True},'prompt':str(prompt.relative_to(root)),'prompt_sha256':sha(prompt),'new_sprite_art_generated_by_script':False,'mirrored':False,'copied_or_interpolated_final_gait':False}
 (root/f'source/walk-{direction}.generation.json').write_text(json.dumps(obj,indent=2),encoding='utf-8')
fixrefs={'fix-phase04-NE.png':root.parent/'30_han_xiangzi/source/fix-phase08-NE-clear.png','fix-phase08-SE.png':root/'references/pose-SE08-single.png'}
fixrefs.update({f'fix-phase{i:02d}-SW.png':root/f'references/pose-SW{i:02d}-single.png' for i in [3,5,6,7]})
fixrefs.update({f'fix-phase{i:02d}-W.png':root/f'references/pose-W{i:02d}-single.png' for i in range(1,9)})
fixrefs['fix-phase03-W.png']=root/'source/fix-phase04-W.png'
fixrefs.update({f'fix-phase{i:02d}-NW.png':root/f'references/pose-NW{i:02d}-single.png' for i in range(1,9)})
for name,reference in fixrefs.items():
 raw=root/'source'/name;prompt=root/'prompts'/name.replace('.png','.txt')
 if not raw.exists():continue
 obj={'source':'Built-in image_gen single-frame retarget preserving approved anatomical pose','raw_sha256':sha(raw),'native_size':list(Image.open(raw).size),'identity_reference':'source/idle.png','identity_sha256':sha(root/'source/idle.png'),'pose_reference':str(reference),'pose_sha256':sha(reference),'prompt_sha256':sha(prompt),'mirror':False,'code_drawn':False}
 raw.with_suffix('.generation.json').write_text(json.dumps(obj,indent=2),encoding='utf-8')
print('source provenance updated')
