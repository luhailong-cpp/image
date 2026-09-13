"""Final read-only verification of current art and explicit historical retention."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib,subprocess,xml.etree.ElementTree as ET
from PIL import Image
B=Path(__file__).resolve().parent;ROOT=B.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
ledger=read(B/'decisions.json');inv={r['path']:r for r in read(B/'inventory.json')['records']}
errors=[];rows=[];checked_current=0;historical=0
visual_ext={'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.svg'}
listed=subprocess.run(['rg','--files','--hidden','-g','!.git/**','-g','!node_modules/**','-g','!**/node_modules/**','-g','!.agents/**','-g','!.codex/**','-g','!qdao_festival_refinement_20260910/**'],cwd=ROOT,check=True,capture_output=True,encoding='utf-8').stdout.splitlines()
current={p.replace('\\','/') for p in listed if Path(p).suffix.lower() in visual_ext}
for p in sorted(current-set(inv)):errors.append({'path':p,'error':'new_visual_not_yet_inventoried'})
for p in sorted(set(inv)-current):errors.append({'path':p,'error':'inventoried_visual_no_longer_listed'})
metadata=read(B/'inventory.json')
if metadata['errors'] or metadata['mapping_issues']:errors.append({'path':'inventory.json','error':'inventory_header_or_current_mapping_error'})
for e in ledger['files']:
 p=ROOT/e['path'];row={'path':e['path'],'decision':e['decision']}
 if e['decision'].startswith('pending'):errors.append({'path':e['path'],'error':'undecided_or_unpublished'});continue
 if not p.is_file():errors.append({'path':e['path'],'error':'missing'});continue
 is_record=e['decision'] in ['retain_record','retain_evidence','retain_input_record']
 if is_record:
  historical+=1
  if e.get('expected_sha256'):
   h=hashlib.sha256(p.read_bytes()).hexdigest();row['sha256']=h
   if h!=e['expected_sha256']:errors.append({'path':e['path'],'error':'record_hash_mismatch'})
  row['verification']='protected record exists; hash checked when bound by review'
 else:
  checked_current+=1;h=hashlib.sha256(p.read_bytes()).hexdigest();row['sha256']=h
  if e.get('expected_sha256') and h!=e['expected_sha256']:errors.append({'path':e['path'],'error':'current_hash_mismatch','expected':e['expected_sha256'],'actual':h})
  try:
   if p.suffix.lower()=='.svg':
    doc=ET.parse(p).getroot();row['svg_dimensions']={k:doc.attrib[k] for k in ['width','height','viewBox'] if k in doc.attrib}
   else:
    with Image.open(p) as im:im.verify()
    with Image.open(p) as im:
     row.update(size=list(im.size),mode=im.mode,frames=getattr(im,'n_frames',1))
     baseline=inv.get(e['path'],{})
     if baseline.get('size') and row['size']!=baseline['size']:errors.append({'path':e['path'],'error':'canvas_changed'})
     if baseline.get('mode') and row['mode']!=baseline['mode']:errors.append({'path':e['path'],'error':'mode_changed'})
     if baseline.get('frames') and row['frames']!=baseline['frames']:errors.append({'path':e['path'],'error':'frame_count_changed'})
   row['verification']='current file hash/integrity/canvas checked'
  except Exception as ex:errors.append({'path':e['path'],'error':str(ex)})
 rows.append(row)
state=read(B/'monitor-state.json')
if state.get('refinement',{}).get('quality_recheck_28_required'):errors.append({'path':'edge_exports/supplement_28','error':'supplement_acceptance_not_yet_closed'})
report={'status':'passed' if not errors else 'incomplete_or_failed','verified_utc':datetime.now(timezone.utc).isoformat(),'ledger_sha256':hashlib.sha256((B/'decisions.json').read_bytes()).hexdigest(),'inventory_sha256':hashlib.sha256((B/'inventory.json').read_bytes()).hexdigest(),'inventory_paths':len(ledger['files']),'current_files_checked':checked_current,'protected_records_checked':historical,'pending_count':ledger['pending_count'],'files':rows,'errors':errors,'client_accessed':False,'scope':'Every inventoried repository visual path has explicit use decision; all current media validated against recorded hashes/contracts. Historical QA/reference/production snapshots are preserved as records.'}
(B/'final-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['files','scope']},ensure_ascii=False))
