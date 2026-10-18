from pathlib import Path
from PIL import Image
import hashlib,json
B=Path(__file__).resolve().parents[1]
T=B/'r15_c06'
src=Path("C:\\Users\\luyua\\.codex\\generated_images\\01a12076-0b9d-76b2-949d-c4cf520a83be\\exec-9b4dfd47-8a60-4875-9efb-8de295332219.png")
seed=T/'pipeline/guides/p02_03.resume-20261016-v01.continuity-seed.png'
out=T/'pipeline/guides/p02_03.resume-20261016-v02.left-native-reinserted-guidance.png'
assert not out.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with Image.open(src) as im:result=im.convert('RGB')
with Image.open(seed) as im:result.paste(im.crop((0,230,230,1254)),(0,230))
result.save(out)
d={'file':str(out),'sha256':sha(out),'gameArt':False,'nativeGeneratedFinal':False,'sourceResampling':False,'operation':'exact crop/paste restored actual selected LEFT230 below TOP230 onto actual unselected generated output; mechanical edit guidance only','sources':[{'file':str(src),'sha256':sha(src)},{'file':str(seed),'sha256':sha(seed),'sourceCrop':[0,230,230,1254],'targetBox':[0,230,230,1254]}],'formalAccepted':False}
Path(str(out)+'.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))

