"""Restore historically hash-bound JSON newline bytes in an isolated evidence copy.

The live candidate gate remains failed. This diagnostic never updates its metadata.
"""
from pathlib import Path
import importlib.util, json, hashlib, shutil, sys
sys.dont_write_bytecode = True
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CHAR='05_celestial_musician_girl'
PACKAGE=ROOT/'qdao_original_roster_v14_hd'
ORIGINAL=PACKAGE/'candidate'/CHAR
SHADOW=HERE/'evidence-shadow'
DEST=SHADOW/'candidate'/CHAR
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(p.read_bytes())
manifest=read(ORIGINAL/'manifest.json');sources=read(ORIGINAL/'processing/frame-sources.json')
paths={'manifest.json','qc.json','processing/scale-profile.json','processing/frame-sources.json'}
expected={'processing/frame-sources.json':manifest['sources_sha256']}
for key,r in sources.items():
    paths.add(key);paths.add(r['source']['path']);paths.add(r['prompt']['path'])
    receipt=r['generation']['receipt'];paths.add(receipt['path']);expected[receipt['path']]=receipt['sha256']
    for stage in r['stages'].values():paths.add(stage['path'])
copies=[]
for rel in sorted(paths):
    source=ORIGINAL/rel;dest=DEST/rel;dest.parent.mkdir(parents=True,exist_ok=True);b=source.read_bytes()
    changed=False;target_hash=expected.get(rel)
    if target_hash and sha_bytes(b)!=target_hash:
        restored=b.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        if sha_bytes(restored)!=target_hash:raise ValueError('Mismatch is not reversible CRLF checkout normalization: '+rel)
        b=restored;changed=True
    dest.write_bytes(b)
    copies.append({'path':rel,'original_sha256':sha(source),'shadow_sha256':sha(dest),'restored_crlf_to_match_historical_hash':changed,'expected_hash':target_hash})
for name in ('generate2dsprite','edge_despill'):
    dest=SHADOW/'tools/vendor'/f'{name}.py';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACKAGE/'tools/vendor'/f'{name}.py',dest)
spec=importlib.util.spec_from_file_location('evidence_shadow_verify',PACKAGE/'tools/verify.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier);verifier.ROOT=SHADOW
results=[]
for key,r in sorted(sources.items()):
    try:result=verifier.verify(CHAR,'NE',False,r['frame'])
    except Exception as error:result={'status':'failed','error':str(error)}
    results.append({'frame':r['frame'],'result':result})
    print(json.dumps({'frame':r['frame'],'status':result['status'],'error':result.get('error')}),flush=True)
report={'character_id':CHAR,'at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'diagnostic independent pixel reconstruction using exact historical hash-matching JSON bytes in isolated copy',
        'live_candidate_gate_status':'failed_Source_mapping_changed',
        'live_candidate_modified':False,'verifier_code_modified':False,'visual_approval':False,
        'copies':copies,'results':results,
        'passed_count':sum(r['result']['status']=='partial_sources_pending_visual' for r in results),
        'restored_json_files':sum(r['restored_crlf_to_match_historical_hash'] for r in copies)}
(HERE/'NE-independent-reconstruction-shadow.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
