from pathlib import Path
import json,subprocess,sys,hashlib
from PIL import Image
root=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_lantern/r08_c10')
ident,source,qa=sys.argv[1:4]
ref=root/'guides'/f'{ident}.input-preview.jpg'; refs=root/'prompts'/f'{ident}.actual-inputs.json'
refs.write_text(json.dumps([ref.as_posix()]),encoding='utf-8')
subprocess.run([sys.executable,str(root/'record_row.py'),ident,source,str(refs),qa],check=True)
p=root/'native'/f'{ident}.record.json';r=json.loads(p.read_text());im=Image.open(root/'native'/f'{ident}.png').convert('RGBA')
assert im.getchannel('A').getextrema()==(255,255)
r['fullOpaque']=True;r['actualToolParameters']={'referenced_image_paths':[ref.as_posix()],'promptFile':r['promptPath']};r['backendModel']='host-managed/unverified'
r['submittedReferenceEncoding']='JPEG quality90 no resize'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
if len(sys.argv)>4:subprocess.run([sys.executable,str(Path(__file__).parent/'prepare_lantern_patch.py'),sys.argv[4]],check=True)
