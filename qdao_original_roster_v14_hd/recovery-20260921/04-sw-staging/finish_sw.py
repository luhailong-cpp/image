"""Archive exact built-in SW14/15/16 evidence; import only to isolated SW staging."""
from pathlib import Path
import importlib.util,json,subprocess,sys,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CHAR='04_mountain_guardian_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v
def fingerprints(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}
before=fingerprints(ROOT/'candidate'/CHAR)
provenance=load('sw_recovery_provenance',ROOT/'tools/inspect_image_provenance.py')
results=[]
for frame in (14,15,16):
 archive=ROOT/f'recovery-20260921/04-generation/SW{frame:02d}-single-v1'
 if not all((archive/p).is_file() for p in ('raw.png','generation-receipt.json')):
  raise RuntimeError(f'Pending actual tool result: {archive}')
 receipt=read(archive/'generation-receipt.json')
 assert receipt['generation_calls']==1 and receipt['paid_api_calls']==0
 exact=receipt['actual_request']['prompt'].encode('utf-8')
 prompt=archive/'prompt.txt'
 if prompt.exists():assert prompt.read_bytes()==exact
 else:prompt.write_bytes(exact)
 prov=provenance.inspect_image(archive/'raw.png')
 if (archive/'provenance.json').exists():assert read(archive/'provenance.json')['sha256']==prov['sha256']
 else:write(archive/'provenance.json',prov)
 out=HERE/'candidate'/CHAR/f'walk/SW/{frame:02d}.png'
 if out.exists():
  record=read(HERE/'candidate'/CHAR/'processing/frame-sources.json')[f'walk/SW/{frame:02d}.png']
  assert record['source']['sha256']==prov['sha256']
 else:
  subprocess.run([sys.executable,'-B',str(ROOT/'recovery-20260921/04-tools/import_local_frame.py'),'--archive',str(archive),'--batch-id',f'SW{frame:02d}-single-v1-local-20260921','--direction','SW','--frame',str(frame),'--staging-root',str(HERE)],check=True)
 results.append({'frame':frame,'raw_sha256':prov['sha256'],'native_size':prov['native_size'],'exact_prompt_sha256':sha(prompt),'output_sha256':sha(out),'validation':read(HERE/'candidate'/CHAR/f'review/validation-SW-{frame:02d}.json')})
assert fingerprints(ROOT/'candidate'/CHAR)==before
write(HERE/'import-summary.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'status':'isolated_sources_verified_visual_pending','frames':results,'canonical_unchanged':True,'generation_calls_this_script':0,'paid_api_calls':0})
