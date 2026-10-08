from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');O=T/'c02-north-repair/original'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for rel in ['native/r01_c02.png','native/r01_c02.png.generation.json','native/r01_c02.prompt.txt','jobs/r01_c02.json','jobs/r01_c02.actual-request.json','jobs/r01_c02.receipt.json']:
 src=T/rel;dst=O/rel;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst);assert sha(src)==sha(dst);items.append({'originalFile':str(src),'archiveFile':str(dst),'sha256':sha(dst),'byteIdentical':True})
im=Image.open(O/'native/r01_c02.png').convert('RGB')
contract={'createdAt':datetime.now(timezone.utc).isoformat(),'baseNative':str(O/'native/r01_c02.png'),'baseSha256':sha(O/'native/r01_c02.png'),'generationRecord':str(O/'native/r01_c02.png.generation.json'),'generationRecordSha256':sha(O/'native/r01_c02.png.generation.json'),'maximumEditableRowsHalfOpen':[0,400],'unchangedRowsHalfOpen':[400,1254],'southDependencyBoxXYXY':[0,1024,1254,1254],'southRawRGBSha256':hashlib.sha256(im.crop((0,1024,1254,1254)).tobytes()).hexdigest(),'futureDerivedOutputConstraint':'Final repair must equal original base for all rows400..1253, including entire lower230 band. Exact east context restoration only within editable rows115..399; current lower east material already passed initial visual QA.','archiveCopies':items,'historicalRecordBytesPreserved':True}
(O/'archive-contract.json').write_text(json.dumps(contract,indent=2),encoding='utf-8');print(json.dumps(contract))

