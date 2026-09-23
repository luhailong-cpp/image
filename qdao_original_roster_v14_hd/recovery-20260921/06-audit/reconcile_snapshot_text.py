"""Restore only exact recorded historical newline bytes in an isolated audit snapshot."""
from pathlib import Path
import hashlib, json, importlib.util
from datetime import datetime, timezone
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHAR = '06_thunder_caster_boy'
OUT = HERE/'candidate'/CHAR
LIVE = ROOT/'candidate'/CHAR
def sha_bytes(value): return hashlib.sha256(value).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value
def tree(path): return {str(p.relative_to(path)):sha_bytes(p.read_bytes()) for p in path.rglob('*') if p.is_file()}
before=tree(LIVE)
rows=[]
for record in read(OUT/'processing/frame-sources.json').values():
    for kind in ('prompt','receipt'):
        binding=record['prompt'] if kind=='prompt' else record['generation']['receipt']
        path=OUT/binding['path']
        current=path.read_bytes()
        expected=binding['sha256']
        if sha_bytes(current)==expected: continue
        transformations={'LF_to_CRLF':current.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'),'CRLF_to_LF':current.replace(b'\r\n',b'\n')}
        matched=[(name,value) for name,value in transformations.items() if sha_bytes(value)==expected]
        if len(matched)!=1: raise RuntimeError(f'No unique exact historical newline recovery: {path}')
        rule,reconstructed=matched[0]
        original=LIVE/binding['path']
        assert original.read_bytes()==current
        rows.append({'frame':record['frame'],'kind':kind,'path':binding['path'],'live_current_sha256':sha_bytes(current),'historical_recorded_sha256':expected,'transformation':rule,'content_equal_after_universal_newlines':current.replace(b'\r\n',b'\n')==reconstructed.replace(b'\r\n',b'\n'),'source_record_sha256':sha_bytes((LIVE/'processing/frame-sources.json').read_bytes()),'only_isolated_snapshot_restored':True})
        path.write_bytes(reconstructed)
write(HERE/'snapshot-text-reconciliation.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'rows':rows,'live_files_unchanged':tree(LIVE)==before,'meaning':'Byte-exact historical prompt/receipt reconstruction in audit copy only; not rewritten live evidence or visual approval.'})
verifier=mod('audit06_text_verifier',ROOT/'tools/verify.py')
verifier.mod=lambda name:mod('audit06_'+name,ROOT/'tools/vendor'/f'{name}.py')
verifier.ROOT=HERE
reports=[]
for frame in (1,2,3,4,5,6,9,13):
    try: result=verifier.verify(CHAR,'E',False,frame)
    except Exception as exc: result={'status':'failed','frame':frame,'error':str(exc)}
    write(HERE/f'validation-E-{frame:02d}-text-reconciled.json',result)
    print(json.dumps(result),flush=True)
    reports.append(result)
assert tree(LIVE)==before
write(HERE/'reconciled-verification-summary.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'all_eight_pixel_rebuilds_passed':all(r['status']=='partial_sources_pending_visual' for r in reports),'report_files':[f'validation-E-{i:02d}-text-reconciled.json' for i in (1,2,3,4,5,6,9,13)],'historical_text_reconstructions':rows,'live_candidate_unchanged':True,'visual_review':'pending','published':False})
