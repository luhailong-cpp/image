from pathlib import Path
import json,hashlib,shutil
from PIL import Image
Z=Path(__file__).resolve().parent;s='r06_c02_yellow_foliage_band_a01'
rp=Z/'receipts'/f'{s}.receipt.json';r=json.loads(rp.read_text());src=Path(r['generatedFile']);out=Z/'rejected'/f'{s}_missing_references.png';out.parent.mkdir(exist_ok=True);assert not out.exists();shutil.copy2(src,out)
d={'stem':s,'status':'REJECTED_reference_submission_error','reason':'references.json uses object.inputs; incorrect caller extraction submitted referenced_image_paths=null. Tool produced an unrelated scene. Do not use as map/native repair. Original receipt is preserved accurately.','actualReferencePaths':r['submitted']['referenced_image_paths'],'actualModel':None,'route':'builtin','archivedOutput':{'path':out.as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'nativeSize':list(Image.open(out).size)},'receipt':{'path':rp.as_posix(),'sha256':hashlib.sha256(rp.read_bytes()).hexdigest()},'selected':False}
p=Z/'qa'/f'{s}_rejection_20261016.json';p.write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d))

