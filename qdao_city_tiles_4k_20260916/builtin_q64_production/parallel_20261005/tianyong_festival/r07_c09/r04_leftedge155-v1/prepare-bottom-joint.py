from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).parent;R=D/'bottom-joint-repair';R.mkdir(exist_ok=True)
prep=json.loads((D/'preparation.json').read_text(encoding='utf-8-sig'))
J=Image.open(D/'final-v2/joined.png').convert('RGBA');B=Image.open(prep['sources']['r08_c09']['file']).convert('RGBA')
A=Image.new('RGBA',(1254,1254));A.paste(J.crop((0,627,1254,1139)),(0,0));A.paste(B.crop((0,0,1254,742)),(0,512));A.convert('RGB').save(R/'native-target.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(R/'preparation.json').write_text(json.dumps({'windowTileLocalLTRB':[0,3584,1254,4838],'nativeScale':1,'sources':[{'file':str(D/'final-v2/joined.png'),'sha256':sha(D/'final-v2/joined.png'),'sourceLTRB':[0,627,1254,1139],'destinationXY':[0,0]},dict(prep['sources']['r08_c09'],sourceLTRB=[0,0,1254,742],destinationXY=[0,512])],'finalUse':'local repair only, explicit mask; do not replace entire external tile'},indent=2))
