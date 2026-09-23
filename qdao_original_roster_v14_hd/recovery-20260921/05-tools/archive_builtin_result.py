"""Archive an actual successful built-in tool result; performs no generation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,shutil,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;GEN=HERE.parent/'05-generation';PACKAGE=HERE.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--original',type=Path,required=True);p.add_argument('--tool-result',type=Path,required=True,help='JSON containing the actual tool output_hint, no invented path');a=p.parse_args()
    archive=a.archive.resolve();assert archive.is_relative_to(GEN),'Archive must be in recovery/05-generation';request=json.loads((archive/'request.json').read_text(encoding='utf-8'))
    result=json.loads(a.tool_result.read_text(encoding='utf-8'));hint=result['output_hint'];original=a.original.resolve()
    assert original.is_file() and str(original) in hint,'Actual original path must occur in the exact tool hint'
    assert request['actual_request'].get('started_at'),'Missing actual request start';assert (archive/'prompt.txt').read_bytes()==request['actual_request']['prompt'].encode('utf-8'),'Prompt mismatch'
    assert not any((archive/name).exists() for name in ('raw.png','generation-receipt.json','provenance.json')),'Existing immutable result; use another attempt directory'
    shutil.copy2(original,archive/'raw.png')
    assert sha(original)==sha(archive/'raw.png')
    receipt={**request,'status':'generated_pending_review','output_hint':hint,'original_generated_file':str(original),'generation_calls':1,'paid_api_calls':0,'completed_at':datetime.now(timezone.utc).isoformat(),'archive_note':'Successful built-in tool result supplied by calling agent; default original retained'}
    (archive/'generation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    spec=importlib.util.spec_from_file_location('musician_provenance',PACKAGE/'tools/inspect_image_provenance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);provenance=m.inspect_image(archive/'raw.png')
    (archive/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'archive':str(archive),'raw_sha256':sha(archive/'raw.png'),'native_size':provenance['native_size'],'original_retained':True,'paid_api_calls':0,'model_actual':'host-managed-unverified'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
