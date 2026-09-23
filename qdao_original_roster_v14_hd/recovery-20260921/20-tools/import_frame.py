"""Import a genuinely generated whole frame through the existing V14 export pipeline."""
from pathlib import Path
import argparse, importlib.util, json, hashlib
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parent
PACKAGE=RECOVERY.parent
CHAR='20_star_formation_master_girl'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--attempt',type=Path,required=True)
    p.add_argument('--slot',required=True)
    p.add_argument('--revision',default='export-v1')
    args=p.parse_args()
    attempt=args.attempt.resolve()
    assert attempt.is_relative_to((RECOVERY/'20-generation').resolve())
    import re
    assert re.fullmatch(r'[a-zA-Z0-9_-]+',args.revision)
    match=re.fullmatch(r'(walk)/(N|NE|E|SE|S|SW|W|NW)/(0[1-9]|1[0-6])\.png',args.slot)
    idle=re.fullmatch(r'idle/(N|NE|E|SE|S|SW|W|NW)\.png',args.slot)
    assert match or idle,'Unknown action slot'
    direction=match[2] if match else idle[1]
    frame=int(match[3]) if match else 0
    out=RECOVERY/'20-work'/args.revision/CHAR
    assert not (out/args.slot).exists(),'Immutable slot: use a new revision for replacements'
    assert (attempt/'raw.png.generation.json').is_file(),'Archive real generation before export'
    spec=importlib.util.spec_from_file_location('star_pipeline',PACKAGE/'tools/pipeline.py')
    pipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipe)
    pipe.output=lambda char: out if char==CHAR else (_ for _ in ()).throw(ValueError('20 only'))
    pipe.preview=lambda: None
    pipe.review=lambda char: None
    pipe.import_sheet(SimpleNamespace(command='import-walk' if match else 'import-idle',character=CHAR,
        direction=direction,source=attempt/'raw.png',prompt=attempt/'prompt.txt',
        receipt=attempt/'generation-receipt.json',batch_id=attempt.name,common_scale=.94,
        chroma_profile='standard',rows=1,cols=1,source_cell_indices=None,idle_order=None,
        output_frames=str(frame) if match else None,start_frame=1))
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    provenance={'file':str(out/args.slot),'sha256':sha(out/args.slot),'derivedFrom':{'path':str(attempt/'raw.png'),
        'sha256':sha(attempt/'raw.png'),'generationRecord':str(attempt/'raw.png.generation.json')},
        'operation':'Existing V14 whole-cell normalization .94, alpha<=8 cleanup, magenta edge despill, fixed feet anchor [512,942]; no new art, no frame interpolation or pose synthesis',
        'processingRecord':str(out/'processing/frame-sources.json'),'visualApproval':False}
    (out/(args.slot+'.generation.json')).write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'slot':args.slot,'path':str(out/args.slot),'sha256':sha(out/args.slot),'visualApproval':False}))

if __name__=='__main__':main()
