from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c10')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
checks=[]
for c in range(1,5):
    cell=f'r02_c{c:02d}';image=B/'native'/f'{cell}.png'
    if not image.exists():continue
    g=read(image.with_suffix('.png.generation.json'));receipt=read(B/'jobs'/f'{cell}.receipt.json')
    assert sha(image)==g['sha256']
    assert g['actualModel'] is None and g['actualQuality'] is None
    assert g['submittedParameters']['model'] is None and g['submittedParameters']['quality'] is None
    assert receipt['prompt']==g['submittedParameters']['prompt']
    assert [r['path'] for r in receipt['references']]==g['submittedParameters']['referenced_image_paths']
    assert sha(g['evidence']['sourceOutputPath'])==g['sha256']
    with Image.open(image) as im:assert im.size==(1254,1254) and im.format=='PNG';size=list(im.size)
    refs=[]
    for ref in g['references']:
        rp=Path(ref['path']);assert rp.exists()
        assert sha(rp)==ref['sha256']
        refs.append({'file':str(rp),'sha256':ref['sha256'],'role':ref['role']})
    checks.append({'cell':cell,'file':str(image),'sha256':g['sha256'],'pixels':size,'receiptPromptMatches':True,'submittedReferencesMatchReceipt':True,'nativeToolSourceHashMatches':True,'actualModel':None,'actualQuality':None,'references':refs})
out=B/'row02-receipt-audit.json'
out.write_text(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'nativeCellsChecked':len(checks),'checks':checks,'scope':'File identity and exact actual submitted evidence only; not a visual approval.','formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'audit':str(out),'cells':len(checks)}))

