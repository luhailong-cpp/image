"""Seal a complete, actually reviewed original-Q character. Default is read-only."""
import argparse,hashlib,importlib.util,json,shutil,sys,uuid
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];DIRS={'N','NE','E','SE','S','SW','W','NW'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def require(v,message):
 if not v:raise ValueError(message)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--character',required=True);p.add_argument('--review-input',required=True,type=Path);p.add_argument('--execute',action='store_true');a=p.parse_args()
 require(a.character and all(c.isalnum() or c in '_-' for c in a.character),'Invalid character ID');out=ROOT/'candidate'/a.character
 spec=importlib.util.spec_from_file_location('original_roster_verify',ROOT/'tools/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);numeric=v.verify(a.character)
 require(not numeric['missing_generation_receipts'],'Save every real generation receipt before approval')
 manifest=read(out/'manifest.json');qc=read(out/'qc.json');review=read(a.review_input);files={r['path']:r['sha256'] for r in manifest['files']}
 require(len(files)==137 and not qc['errors'],'Complete, numerically valid character required')
 require(review.get('status')=='passed' and review.get('reviewed_input_manifest_sha256')==sha(out/'manifest.json') and review.get('reviewed_input_qc_sha256')==sha(out/'qc.json'),'Fresh visual review must bind the current inspected candidate')
 require(review.get('reviewed_artifacts')==files,'Visual review must bind the exact137 PNGs')
 require(set(review.get('reviewed_directions',[]))==DIRS and set(review.get('notes_by_direction',{}))==DIRS and all(str(n).strip() for n in review['notes_by_direction'].values()),'Specific visual notes for all eight directions are required')
 for name in ('normal_size_review','enlarged_review','seam_15_16_01_review','anatomical_contacts_01_09_review','native_resolution_review','closeup_1080p_review'):require(review.get(name) is True,f'Missing actual inspection: {name}')
 for name in ('native_resolution_notes','closeup_1080p_notes'):require(str(review.get(name,'')).strip(),f'Explicit HD inspection notes required: {name}')
 require(review.get('evidence'),'Saved visual evidence required')
 for item in review['evidence']:
  path=Path(item['path']);path=path if path.is_absolute() else a.review_input.parent/path;require(path.is_file() and sha(path)==item['sha256'],'Visual evidence changed or missing')
 if not a.execute:print(json.dumps({'status':'ready_dry_run','character':a.character,'pngs':137,'writesPerformed':False}));return
 history=out/'review/approval-history'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);history.mkdir(parents=True)
 names=('manifest.json','qc.json','processing/frame-sources.json','review/visual-review.json','validation.json');existing={name:(out/name).exists() for name in names}
 for name in names:
  if existing[name]:dst=history/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/name,dst)
 shutil.copy2(a.review_input,history/'fresh-review-input.json')
 try:
  records=read(out/'processing/frame-sources.json')
  for record in records.values():record['visual_review']='passed';record['generation']['status']='passed_internal_visual_review'
  write(out/'processing/frame-sources.json',records);manifest['sources_sha256']=sha(out/'processing/frame-sources.json');manifest['status']='passed';manifest['visual_review']='passed';qc['status']='passed';qc['visual_review']='passed'
  for direction_qc in qc['directions'].values():direction_qc['status']='passed';direction_qc['visual_review']='passed'
  write(out/'manifest.json',manifest);write(out/'qc.json',qc)
  final={**review,'reviewed_manifest_sha256':sha(out/'manifest.json'),'reviewed_qc_sha256':sha(out/'qc.json'),'review_input_sha256':sha(a.review_input),'sealed_at_utc':datetime.now(timezone.utc).isoformat()};write(out/'review/visual-review.json',final)
  validation=v.verify(a.character,require_visual=True);write(out/'validation.json',validation)
  print(json.dumps({'status':'passed','character':a.character,'manifest_sha256':sha(out/'manifest.json'),'qc_sha256':sha(out/'qc.json'),'validation_sha256':sha(out/'validation.json'),'history':str(history)}))
 except Exception:
  for name in names:
   current=out/name
   if current.exists():failed=history/'failed'/name;failed.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(current,failed)
   if existing[name]:shutil.copy2(history/name,current)
   elif current.exists():current.unlink()
  raise
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'status':'blocked','error':str(e)}),file=sys.stderr);sys.exit(1)
