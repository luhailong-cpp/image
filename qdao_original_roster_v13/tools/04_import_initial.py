from pathlib import Path
from PIL import Image
import subprocess,sys
root=Path(r'E:/work/image/qdao_original_roster_v13'); char='04_mountain_guardian_boy'
for stem,frames in [('walk-E-nearleg-pair-v1','1,13'),('walk-E-farleg-pair-v1','9,5')]:
 d=root/'generation'/char/stem
 subprocess.run([sys.executable,'-B',str(root/'tools/pipeline.py'),'import-walk','--character',char,'--direction','E','--source',str(d/'raw.png'),'--prompt',str(d/'prompt.txt'),'--receipt',str(d/'receipt.json'),'--batch-id',stem,'--rows','1','--cols','2','--output-frames',frames,'--common-scale','.84'],check=True)
for p in (root/'generation'/char/'S-anchors').glob('*.png'):
 Image.open(p).convert('RGB').save(p.with_suffix('.jpg'),quality=91)
subprocess.run([sys.executable,'-B',str(root/'tools/pipeline.py'),'portrait','--character',char,'--source',str(root/'baseline/q_daoist_character_pack_4096/04_mountain_guardian_boy_transparent_4096.png')],check=True)
