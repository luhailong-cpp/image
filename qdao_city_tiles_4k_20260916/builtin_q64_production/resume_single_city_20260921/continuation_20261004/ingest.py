"""Save a real built-in return and its provenance; never generates or resizes pixels."""
import argparse, datetime, hashlib, json, shutil
from pathlib import Path
from PIL import Image

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument('directory')
ap.add_argument('source')
a = ap.parse_args()
run = Path(a.directory).resolve()
repo = next(p for p in run.parents if (p/'config/image-generation.json').is_file())
request = json.loads((run/'request.json').read_text(encoding='utf-8-sig'))
receipt = json.loads((run/'tool-response.json').read_text(encoding='utf-8-sig'))
source = Path(a.source)
target = run/'native.png'
assert not target.exists()
shutil.copyfile(source, target)
with Image.open(target) as im:
    im.load()
    width, height, mode = im.width, im.height, im.mode
config = json.loads((repo/'config/image-generation.json').read_text(encoding='utf-8-sig'))
prompt = run/'prompt.txt'
prompt.write_text(request['payload']['prompt']+'\n', encoding='utf-8')
refs = [{'file':p,'sha256':sha(p),'role':'edit target and exact geometry' if i == 0 else 'approved art style only'} for i,p in enumerate(request['payload']['referenced_image_paths'])]
record = dict(schemaVersion=1, file=str(target), sha256=sha(target), width=width, height=height, format='PNG', mode=mode,
    generatedAt=None, hostObservedStartedAtUtc=receipt['hostObservedStartedAtUtc'], hostObservedFinishedAtUtc=receipt['hostObservedFinishedAtUtc'],
    recordedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), tool='image_gen.imagegen',route='builtin',configSnapshot=config,
    submittedParameters={'model':None,'quality':None,'size':None},actualModel=None,actualQuality=None,
    unverifiedReason='Host-managed built-in route: tool exposes no model/quality/size selectors and returned no actual model/quality or server generation time.',
    prompt=str(prompt),references=refs,sourceCropLTRB=request.get('cropLTRB'),editSourceCandidateSha256=request.get('sourceCandidateSha256'),
    requestedNativePixels=request.get('desiredNativePixels'),rawReturnedPixels=[width,height],localResizingPerformed=False,
    evidence={'receipt':str(run/'tool-response.json'),'receiptSha256':sha(run/'tool-response.json'),'request':str(run/'request.json'),'requestSha256':sha(run/'request.json'),'hostSavedOriginal':str(source),'hostSavedOriginalSha256':sha(source),'byteIdenticalCopy':sha(source)==sha(target)},formalAccepted=False)
(run/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(target),'sha256':sha(target),'pixels':[width,height]},ensure_ascii=False))
