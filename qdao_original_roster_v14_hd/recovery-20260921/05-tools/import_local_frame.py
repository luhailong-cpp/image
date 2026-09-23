"""Import only 05 NE03/NE16 into isolated staging; no canonical-write option."""
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, re, shutil, sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parent
PACKAGE=RECOVERY.parent
IMAGE_ROOT=PACKAGE.parent
CHARACTER='05_celestial_musician_girl'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def require(v,message):
    if not v:raise ValueError(message)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def binding(archive):
    raw=archive/'raw.png';prompt=archive/'prompt.txt';receipt_path=archive/'generation-receipt.json';provenance_path=archive/'provenance.json'
    require(all(p.is_file() for p in (raw,prompt,receipt_path,provenance_path)),'Need raw, exact prompt, completed receipt and provenance')
    receipt=read(receipt_path);provenance=read(provenance_path);request=receipt.get('actual_request',{})
    require(receipt.get('tool')=='built-in image_gen' and receipt.get('generation_calls')==1 and receipt.get('paid_api_calls')==0,'Require exactly one successful built-in call and zero paid calls')
    require(prompt.read_bytes()==request.get('prompt','').encode('utf-8'),'Exact prompt bytes differ from actual request')
    require(request.get('started_at') and receipt.get('completed_at'),'Missing actual call timestamps')
    require(receipt.get('output_hint') and receipt.get('original_generated_file'),'Missing genuine tool output hint/default original path')
    original=Path(receipt['original_generated_file'])
    require(original.is_file() and sha(original)==sha(raw),'Default generated original must exist and match archived raw')
    require(sha(raw)==provenance.get('sha256'),'Raw/provenance SHA mismatch')
    refs=request.get('referenced_image_paths',[]);require(1<=len(refs)<=3,'Use one to three actual local references')
    references=[]
    for value in refs:
        p=Path(value).resolve();require(p.is_relative_to(IMAGE_ROOT) and p.is_file(),'Reference must be an existing file in this local image workspace')
        references.append({'path':str(p),'sha256':sha(p)})
    start_bindings=receipt.get('reference_bindings_at_start',[])
    if start_bindings:
        expected={str(Path(r['path']).resolve()):r['sha256'] for r in start_bindings}
        require(all(expected.get(r['path'])==r['sha256'] for r in references),'Reference bytes changed after actual request preparation')
    with Image.open(raw) as image:size=list(image.size)
    require(size==provenance.get('native_size') and min(size)>=1024,'Native single frame must be at least1024 in each dimension')
    return {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'raw_sha256':sha(raw),'native_size':size,'prompt_sha256':sha(prompt),'receipt_sha256':sha(receipt_path),'provenance_sha256':sha(provenance_path),'original_generated_file':str(original),'original_sha_matches':True,'references':references,'model_actual':'host-managed-unverified','paid_api_calls':0,'visual_review':'pending'}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--batch-id',required=True)
    parser.add_argument('--frame',type=int,choices=(3,16),required=True)
    parser.add_argument('--staging-root',type=Path,required=True)
    args=parser.parse_args();require(re.fullmatch(r'[A-Za-z0-9_-]+',args.batch_id),'Invalid batch ID')
    archive=args.archive.resolve();stage=args.staging_root.resolve()
    require(archive.is_relative_to(RECOVERY/'05-generation'),'Archive must remain in this recovery/05-generation directory')
    require(stage.is_relative_to(archive) or stage.is_relative_to(HERE),'Staging must be inside this frame archive or 05-tools')
    out=stage/'candidate'/CHARACTER
    require(not (out/'manifest.json').exists(),'Use a fresh per-attempt staging root; do not overwrite any existing manifest')
    evidence=binding(archive)
    pipe=module('musician_staging_pipeline',PACKAGE/'tools/pipeline.py')
    pipe.output=lambda character:out if character==CHARACTER else (_ for _ in ()).throw(ValueError('05 only'))
    pipe.preview=lambda:None
    pipe.import_sheet(SimpleNamespace(command='import-walk',character=CHARACTER,direction='NE',source=archive/'raw.png',prompt=archive/'prompt.txt',receipt=archive/'generation-receipt.json',batch_id=args.batch_id,common_scale=.84,chroma_profile='purple-preserve',rows=1,cols=1,source_cell_indices=None,idle_order=None,output_frames=str(args.frame),start_frame=1))
    verifier=module('musician_staging_verifier',PACKAGE/'tools/verify.py');verifier.ROOT=stage
    verifier.mod=lambda name:module('musician_verify_'+name,PACKAGE/'tools/vendor'/f'{name}.py')
    validation=verifier.verify(CHARACTER,'NE',False,args.frame)
    output=out/f'walk/NE/{args.frame:02d}.png';record=read(out/'processing/frame-sources.json')[f'walk/NE/{args.frame:02d}.png']
    require(record['chroma_thresholds']==[50,75] and record['common_scale']==.84,'Purple-preserve profile/scale changed')
    write(out/f'review/validation-NE-{args.frame:02d}.json',validation)
    write(out/'recovery-bindings'/args.batch_id/'source-binding.json',evidence)
    result={'character':CHARACTER,'slot':f'walk/NE/{args.frame:02d}.png','output':str(output),'output_sha256':sha(output),'common_scale':.84,'chroma_thresholds':[50,75],'single_frame_reconstruction':validation,'canonical_modified':False,'visual_review':'pending','can_publish':False}
    write(out/'recovery-bindings'/args.batch_id/'import-result.json',result)
    im=Image.open(output).convert('RGBA')
    for name,color in [('dark',(30,38,46)),('light',(240,238,228))]:
        canvas=Image.new('RGB',(1024,1088),color);canvas.paste(im,(0,48),im);ImageDraw.Draw(canvas).text((16,16),f'05 NE{args.frame:02d} / purple-preserve50/75 / fixed.84 / pending',fill='white' if name=='dark' else 'black');dest=out/f'review/backgrounds/NE{args.frame:02d}-{name}.png';dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
