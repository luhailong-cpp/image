from pathlib import Path
import json,sys,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z));import tile_native_workflow as wf
pid,v=sys.argv[1:3];wf.writable_tile(T.name);receipt=wf.read(T/f'{pid}-{v}.receipt.json');src=Path(receipt['sourcePath']);dest=T/'native'/f'{pid}-{v}.png'
assert src.exists();assert wf.Image.open(src).size==(1254,1254)
if dest.exists():
 assert wf.sha(dest)==wf.sha(src),'Existing version differs; do not overwrite'
 assert dest.with_suffix('.png.generation.json').exists(),'Existing source lacks provenance; review first'
else:wf.ingest(T.name,pid,v,str(src))
p=T/'selected-patches.json';sel=wf.read(p);backup=T/'qa'/f'selection-before-{pid}-{v}-20261016.json'
assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,backup)
sel['patches'][pid]=dest.relative_to(T).as_posix();sel.update(status='native_production_material_QA_pending',internalReady=False,formalAccepted=False,materialPending=True,updatedAt=datetime.now(timezone.utc).isoformat());wf.write(p,sel)
print(json.dumps({'tile':T.name,'patch':pid,'version':v,'native':str(dest),'sha256':wf.sha(dest),'selectedPositions':len(sel['patches']),'sourcePath':str(src)}))
