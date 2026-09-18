"""Re-key only 05 from unchanged genuine source cells; all pose pixels are generated art."""
from pathlib import Path
import json,sys,shutil,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];c=ROOT/'candidate/05_celestial_musician_girl';history=ROOT/'history/05-before-purple-preserve-20260917'
rs=json.loads((c/'processing/frame-sources.json').read_text(encoding='utf-8-sig'))
assert all(r['chroma_thresholds']==[100,150] for r in rs.values()),'One-time reprocessing starts at original profile only'
assert not history.exists(),'Backup already exists; inspect before rerunning'
shutil.copytree(c,history)
groups={}
for r in rs.values():
 key=(r['kind'],r['direction'] if r['kind']=='walk' else None,r['source']['path']);groups.setdefault(key,[]).append(r)
plan=[]
for (kind,d,path),values in groups.items():
 values.sort(key=lambda r:r['source']['cell_index']);r=values[0];rows,cols=r['source']['grid'];bid=Path(path).parent.name
 command=[sys.executable,'-B',str(ROOT/'tools/pipeline.py'),'import-'+kind,'--character','05_celestial_musician_girl','--chroma-profile','purple-preserve','--rows',str(rows),'--cols',str(cols),'--source',str(c/path),'--prompt',str(c/r['prompt']['path']),'--receipt',str(c/r['generation']['receipt']['path']),'--batch-id',bid]
 if kind=='walk':command+=['--direction',d,'--source-cell-indices',','.join(str(x['source']['cell_index']) for x in values),'--output-frames',','.join(str(x['frame']) for x in values)]
 elif rows==1 and cols==1:command+=['--direction',r['direction']]
 else:command+=['--idle-order',','.join(x['direction'] for x in values)]
 plan.append({'batch':bid,'direction':d,'kind':kind,'command':command,'source_sha256':r['source']['sha256']})
(c/'review/chroma-reprocess-plan.json').write_text(json.dumps({'reason':'Original100/150 erased authentic lavender pants; conservative50/75 preserves source alpha/material. No pose changes.','backup':str(history),'items':plan},indent=2)+'\n',encoding='utf-8')
for item in plan:
 print('REPROCESS '+item['batch'],flush=True);subprocess.run(item['command'],cwd=ROOT,check=True)
print('REPROCESS COMPLETE',flush=True)
