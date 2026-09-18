"""Bind a new full input snapshot to the already staged reviewed candidates; not runtime proof."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[1]
PROJECT=Path('E:/work/tmp/qdao-original-live-candidate-20260917')
FORMAL=Path('E:/work/mmorpg-client')
FAMILY='Assets/Resources/World/Characters/QdaoOriginalRosterV13'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['editmode','playmode'],required=True);p.add_argument('--character',action='append',required=True);a=p.parse_args()
snapshot=RUN/('input-'+a.phase+'.json');data=read(snapshot);require(Path(data['project']).resolve()==PROJECT.resolve(),'Wrong input project');require(set(data['included_roots'])=={'Assets','Packages','ProjectSettings','Library/PackageCache'},'Incomplete input roots');rows={r['path']:r for r in data['files']};require(len(rows)==data['count'],'Duplicated snapshot inventory')
spec=importlib.util.spec_from_file_location('binding_contract',ROOT/'tools/publish_original_roster_v13.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
for k in contract.CODE_PATHS:
 require(k in rows and rows[k]['sha256']==sha(PROJECT/k)==sha(FORMAL/k),'Actual source changed from captured/tested source '+k)
plans={}
for folder in [RUN.parent/'accepted-originals-run1',RUN.parent/'accepted-originals-run2',RUN]:
 for report in folder.glob('stage*-execute.json'):
  d=read(report);require(d['status']=='completed' and d['writesPerformed'],'Unsuccessful stage report');
  for item in d['candidates']:plans[item['characterId']]=item
inventory={x['character_id'] for x in read(ROOT/'inventory.json')['characters']}
require(len(set(a.character))==len(a.character) and set(a.character).issubset(inventory),'Invalid requested identities')
checked=[]
for character in a.character:
 require(character in plans,'No actual completed stage '+character);plan=plans[character];candidate=ROOT/'candidate'/character;manifest=read(candidate/'manifest.json');require(manifest['status']==manifest['visual_review']=='passed','Candidate no longer approved')
 expected={row['path']:row['sha256'] for row in manifest['files']};require(len(expected)==145,'Wrong PNG inventory');expected.update({'manifest.json':plan['manifestSha256'],'validation.json':plan['validationSha256'],'appearance.json':plan['appearanceSha256']})
 require(sha(candidate/'manifest.json')==plan['manifestSha256'] and sha(candidate/'qc.json')==plan['qcSha256'] and sha(candidate/'validation.json')==plan['validationSha256'],'Stage candidate revision changed')
 prefix=FAMILY+'/'+character+'/'
 actual={path.relative_to(PROJECT).as_posix() for path in (PROJECT/(FAMILY+'/'+character)).rglob('*') if path.is_file() and not path.name.endswith('.meta')}
 require(actual=={prefix+k for k in expected},'Actual staged inventory differs '+character)
 for relative,digest in expected.items():
  key=prefix+relative;require(key in rows and rows[key]['sha256']==digest==sha(PROJECT/key),'Actual/input/staged bytes differ '+key);checked.append({'path':key,'sha256':digest})
actual_ids={p.name for p in (PROJECT/FAMILY).iterdir() if p.is_dir()};require(actual_ids==set(a.character),'Unexpected Original family present '+repr(actual_ids))
result={'status':'passed_snapshot_candidate_source_binding','created_utc':datetime.now(timezone.utc).isoformat(),'scope':'SHA binding of captured inputs and actual project to completed stage; not Unity test acceptance','input_snapshot_sha256':sha(snapshot),'characters':a.character,'resource_count':len(checked),'resource_files':checked,'core_source_count':len(contract.CODE_PATHS),'snapshot_count':data['count'],'comparison_counts':{k:len(data.get('comparison',{}).get(k,[])) for k in ('added','removed','changed')},'binding_tool_sha256':sha(Path(__file__))}
out=RUN/('input-'+a.phase+'-binding.json');require(not out.exists(),'Keep prior binding record');out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='resource_files'}))
