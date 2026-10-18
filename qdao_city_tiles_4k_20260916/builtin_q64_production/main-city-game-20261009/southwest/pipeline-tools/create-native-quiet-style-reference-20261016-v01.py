from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1];src=B/'r14_c06/native/p03_01.png';out=B/'pipeline-tools/native-quiet-gray-style-20261016-v01.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(src)=='e1118b0ea3703f3a7aaa96c5ce647ea0a9b7b1db2b1e5bfde0b22474adf93207' and not out.exists()
Image.open(src).convert('RGB').crop((600,650,1100,1150)).save(out)
out.with_suffix('.derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':sha(src),'crop':[600,650,1100,1150],'purpose':'native stone material reference only, never a full patch or final4k','sourceResampling':False,'sha256':sha(out)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)

