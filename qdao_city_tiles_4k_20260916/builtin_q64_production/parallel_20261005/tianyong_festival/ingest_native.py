"""Save actual built-in result unchanged; do not automatically accept or splice it."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
from PIL import Image

TASK=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('patch_dir',type=Path);ap.add_argument('host_path',type=Path)
    args=ap.parse_args();d=args.patch_dir.resolve();d.relative_to(TASK)
    request=read(d/'request.json');prep=read(d/'preparation.json')
    receipt=d/'tool-response.json';assert receipt.is_file()
    dest=d/'native.png';assert not dest.exists()
    with Image.open(args.host_path) as im:im.verify()
    shutil.copy2(args.host_path,dest);assert sha(dest)==sha(args.host_path)
    with Image.open(dest) as im:
        im.load();width,height=im.size;fmt=im.format
    record={'file':str(dest),'sha256':sha(dest),'generatedAt':None,'observedCompletionAt':datetime.now(timezone.utc).isoformat(),'width':width,'height':height,'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':request['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; no model, quality or size selector in the tool; response supplies no verifiable backend model or quality. Server generation time is not provided.','prompt':str(d/'prompt.txt'),'references':prep['references'],'referenceRoles':['edit target: exact native context and missing transparent region','canonical layout only; enlarged reference pixels forbidden in output','primary approved rendering style only'],'evidence':{'actualToolResponse':{'file':str(receipt),'sha256':sha(receipt)},'actualRequest':{'file':str(d/'request.json'),'sha256':sha(d/'request.json')},'hostSavedOutput':str(args.host_path),'hostOutputSha256':sha(args.host_path),'copiedByteIdentically':True},'candidateStatus':'unreviewed_native_return','countsAsComplete4KTile':False,'formalAccepted':False}
    (d/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (TASK/'current-work.json').write_text(json.dumps({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_return_saved_visual_review_pending','tile':request['tile'],'patch':request['patch'],'file':str(dest),'sha256':sha(dest),'pixels':[width,height],'wholeCityComplete':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file':str(dest),'pixels':[width,height],'sha256':sha(dest),'formalAccepted':False}))
if __name__=='__main__':main()
