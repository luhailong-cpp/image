"""Validate planned references; --start records a request but never calls image APIs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent;GEN=HERE.parent/'05-generation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--slot',choices=('NE03','NE16'),required=True);p.add_argument('--start',action='store_true');a=p.parse_args()
    archive=GEN/f'{a.slot}-pose-v2';template=json.loads((archive/'request-template.json').read_text(encoding='utf-8'));prompt=(archive/'prompt.txt').read_bytes().decode('utf-8')
    refs=template['actual_request']['referenced_image_paths'];bindings=[]
    for value in refs:
        path=Path(value);assert path.is_file(),'Missing reference: '+value;bindings.append({'path':value,'sha256':sha(path)})
    assert prompt==template['actual_request']['prompt'],'Template/prompt bytes disagree'
    if a.start:
        target=archive/'request.json';assert not target.exists(),'Do not overwrite an existing actual request; create a new attempt directory'
        template['actual_request']['started_at']=datetime.now(timezone.utc).isoformat();template['status']='request_prepared_not_yet_submitted';template['reference_bindings_at_start']=bindings
        with target.open('x',encoding='utf-8') as f:f.write(json.dumps(template,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'slot':a.slot,'status':'request_prepared_not_submitted' if a.start else 'planned_references_validated_no_call','prompt_sha256':sha(archive/'prompt.txt'),'references':bindings,'image_generation_called':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
