from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
TILE=ROOT/'r09_c09'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
notes={
 'r04_c04':'Dense rounded green canopy and lower-right trunk kept. First native output added thin diagonal pavement grid in exposed left gaps; second builtin edit removed grid while preserving leaf/trunk layout. Root actually viewed guide, approved style, first output and edited output. The rejected first output remains part of the edit ancestry, not direct assembly.',
 'r04_c03':'Existing cropped tall red lacquer lantern with blank gold inset, curled red arms and small gold beads continues outside bottom; green leaf outline at right. Root viewed guide/style and actual output. No text, new objects or fine pavement grid.',
 'r04_c02':'Existing one curved brown upper stone groove, right cropped red arm and lavender-grey lantern shadow. Root viewed guide and actual output with approved style attached. Broad low-contrast stone facets remain; assembled seam review separate.',
 'r04_c01':'One upper curved brown stone groove and joining near-vertical groove, no new objects. Root viewed guide and actual output; approved style actually viewed and attached. Broad low-contrast stone facets visible; assembled seam review separate.'}
items=[]
for cell in ('r04_c04','r04_c03','r04_c02','r04_c01'):
 gp=TILE/'native'/f'{cell}.png.generation.json';g=read(gp);p=Path(g['file']);rp=Path(g['evidence']['toolResultPath']);r=read(rp)
 assert sha(p)==g['sha256']==sha(g['evidence']['sourceOutputPath'])
 assert Image.open(p).size==(1254,1254)
 assert sha(rp)==g['evidence']['toolResultSha256']
 assert sha(g['prompt'])==g['promptSha256'] and Path(g['prompt']).read_text(encoding='utf-8')==r['prompt']
 assert sha(g['sourceJob'])==g['sourceJobSha256']
 assert g['actualModel'] is None and g['actualQuality'] is None
 for ref in g['references']:assert sha(ref['path'])==ref['sha256']
 items.append({'cell':cell,'native':str(p),'sha256':sha(p),'generationRecord':str(gp),'generationRecordSha256':sha(gp),'actualReceipt':str(rp),'actualReceiptSha256':sha(rp),'guideAndStyleAndOutputActuallyViewed':True,'observation':notes[cell],'sourceAndEvidenceHashesVerified':True,'fullSeamAcceptance':False})
out=TILE/'worker-row04.json';assert not out.exists()
out.write_text(json.dumps({'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c09','worker':'root','row':4,'nativeCount':4,'actualBuiltinCalls':5,'rejectedNativeCount':1,'rejectionIsSelectedAIEditAncestor':True,'rejectedEvidence':str(TILE/'jobs/r04_c04.attempt01.generation.json'),'items':items,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out),'selected':4,'actualCalls':5}))
