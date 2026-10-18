"""Persist one already-returned builtin north image; never calls AI or shared progress."""
from pathlib import Path
import sys, importlib.util
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import production as p
from PIL import Image
spec=importlib.util.spec_from_file_location('north_worker',ROOT/'qa/expansion-north-worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
stem,source,note=sys.argv[1:4]
assert stem.startswith('r08_')
dest=ROOT/'native'/(stem+'.png')
receipt=ROOT/'receipts'/(stem+'.tool.json')
if not receipt.exists():
    p.dump(receipt,{'tool':'image_gen.imagegen','route':'builtin','recordedAtUtc':p.now(),'outcome':'success','sourceToolPath':source,'actualModel':None,'actualQuality':None,'submittedReferenceCount':4})
if not dest.exists():
    w.ingest(stem,source)
else:
    assert p.hashfile(dest)==p.hashfile(source),'Existing output differs, preserve both and audit'
with Image.open(dest) as im:assert im.size==(1254,1254)
reqp=ROOT/'prompts'/(stem+'.request.json');req=p.load(reqp)
assert all(p.hashfile(r['path'])==r['sha256'] for r in req['references'])
recp=Path(str(dest)+'.generation.json');rec=p.load(recp)
req.update(submitted=True,promptSha256=p.hashfile(rec['prompt']))
req.setdefault('submittedAtUtc',p.load(receipt)['recordedAtUtc'])
p.dump(reqp,req)
rec['promptSha256']=req['promptSha256'];rec['receiptSha256']=p.hashfile(receipt)
p.dump(recp,rec)
if 'subrow' in rec['coordinates']:w.select(stem,note)
d=w.state();d['inFlight']=False;d['updatedAtUtc']=p.now();d['nextStep']='Continue native gaps along stable adjacent edges';w.save(d)
print(p.hashfile(dest))

