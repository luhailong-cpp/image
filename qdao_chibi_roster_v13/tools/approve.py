"""Seal a complete visually reviewed V13 candidate; defaults to dry run."""
import argparse, hashlib, importlib.util, json, shutil, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'candidate/24_lu_dongbin'
DIRS={'N','NE','E','SE','S','SW','W','NW'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def require(v,message):
    if not v:raise ValueError(message)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review-input',required=True,type=Path);p.add_argument('--execute',action='store_true');a=p.parse_args()
    spec=importlib.util.spec_from_file_location('verify_for_approval',ROOT/'tools/verify.py');verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    # Previous visual approval cannot approve changed art. A fresh external review input is mandatory below.
    numeric=verifier.verify(require_visual=False,ignore_previous_visual=True)
    review=read(a.review_input)
    require(review.get('status')=='passed' and review.get('reviewed_input_manifest_sha256')==sha(OUT/'manifest.json') and review.get('reviewed_input_qc_sha256')==sha(OUT/'qc.json'),'Fresh visual review must bind the currently inspected candidate manifest and QC')
    expected={r['path']:r['sha256'] for r in numeric['artifacts']}
    require(review.get('reviewed_artifacts')==expected and len(expected)==145,'Visual review must identify all 145 exact delivery PNGs')
    require(set(review.get('reviewed_directions',[]))==DIRS and set(review.get('notes_by_direction',{}))==DIRS and all(str(v).strip() for v in review['notes_by_direction'].values()),'All eight directions need specific visual notes')
    for field in ('normal_size_review','enlarged_review','seam_15_16_01_review','anatomical_contacts_01_09_review'):require(review.get(field) is True,f'Missing visual check: {field}')
    evidence=review.get('evidence',[]);require(evidence,'Saved visual evidence is required')
    for item in evidence:
        path=Path(item['path']);path=path if path.is_absolute() else a.review_input.parent/path
        require(path.is_file() and sha(path)==item['sha256'],f'Visual evidence is missing/changed: {path}')
    if not a.execute:
        print(json.dumps({'status':'ready_dry_run','pngs':145,'visualReviewInputSha256':sha(a.review_input),'writesPerformed':False}));return
    history=OUT/'review/approval-history'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);history.mkdir(parents=True)
    names=('manifest.json','qc.json','review/visual-review.json','validation.json');existed={}
    for name in names:
        src=OUT/name;existed[name]=src.exists()
        if src.exists():
            dst=history/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    shutil.copy2(a.review_input,history/'fresh-review-input.json')
    try:
        manifest=read(OUT/'manifest.json');qc=read(OUT/'qc.json')
        manifest['status']='passed';qc['status']='passed';qc['visual_review']='passed'
        write(OUT/'manifest.json',manifest);write(OUT/'qc.json',qc)
        sealed={**review,'reviewed_manifest_sha256':sha(OUT/'manifest.json'),'reviewed_qc_sha256':sha(OUT/'qc.json'),'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'review_input_sha256':sha(a.review_input),'review_input_archive':str(history/'fresh-review-input.json')}
        write(OUT/'review/visual-review.json',sealed)
        result=verifier.verify(require_visual=True);write(OUT/'validation.json',result)
        require(result['status']=='passed','Sealed candidate did not independently verify')
        print(json.dumps({'status':'passed','manifestSha256':sha(OUT/'manifest.json'),'qcSha256':sha(OUT/'qc.json'),'validationSha256':sha(OUT/'validation.json'),'visualReviewSha256':sha(OUT/'review/visual-review.json'),'history':str(history)}))
    except Exception:
        # Keep failed metadata as evidence and restore every prior byte; never alter PNGs.
        for name in names:
            current=OUT/name
            if current.exists():
                failed=history/'failed'/name;failed.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(current,failed)
            if existed[name]:shutil.copy2(history/name,current)
            elif current.exists():current.unlink()
        raise
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'blocked','error':str(e)}),file=sys.stderr);sys.exit(1)
