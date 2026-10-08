"""Prepare p44 through the approved NE adapter and attach its exact extra E round-post reference."""
from pathlib import Path
import sys,contextlib,io
F=Path(__file__).resolve().parent;ROOT=F.parent
sys.path.insert(0,str(ROOT/'tools/multi_edge'));import cli
from production import read,write,sha
plan=read(F/'plan.json');extra=plan['nativePatchAdditionalReferences']['p44'][0]
assert sha(extra['file'])==extra['sha256']
# Initial adapter output is replaced below before any AI call. Existing/in-flight p44 is refused by cli.prepare.
with contextlib.redirect_stdout(io.StringIO()):cli.prepare('r10_c11',4,4)
out=F/'native';pp=out/'p44.prompt.txt';callpath=out/'p44.call.json';rp=out/'p44.request.json'
call=read(callpath);request=read(rp)
prompt=call['prompt']+'\nImage4 is an EXACT UNRESIZED crop of the existing EAST neighbor. The clipped ROUND fence post at its LEFT edge is the authoritative continuation for Image1 right-side native strip. Its rounded cap, shaft thickness, circular collars and gold highlights must continue as one complete ROUND post into this new tile. Ignore the unrelated background foliage as a layout change. Delete the soft guide pointed cone faces and square shaft from the connecting post; do not keep a left pointed half. Keep Image1 crop, all other footprints and real native boundary endpoints unchanged.'
pp.write_text(prompt,encoding='utf-8');call['prompt']=prompt
call['referenced_image_paths'].append(extra['file']);write(callpath,call)
request['submittedParameters'].update(call);request['promptSha256']=sha(pp)
request['references'].append(extra)
request['additionalReferencePreparation']={'file':str(Path(__file__).resolve()),'sha256':sha(__file__)}
write(rp,request)
print(str(callpath))

