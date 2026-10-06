from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib,json,shutil
base=Path(__file__).resolve().parent
source=Path('C:/Users/luyua/.codex/generated_images/01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1/exec-e1588dc2-5b62-4a98-8474-a95b9a96a7b8.png')
target=base/'native.png'
assert not target.exists()
shutil.copyfile(source,target)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=json.loads((base/'tool-result.json').read_text(encoding='utf-8'))
refs=[{'path':str(base.parent/'guides/regional-layout-only-preview-1254.png'),'role':'shared day macro geometry with exact spring c09 west anchor; layout-only guide'}, {'path':'D:/work/image/designs/gameplay-ui/04-guild.png','role':'primary user confirmed style, not geometry'}]
for ref in refs: ref['sha256']=sha(ref['path'])
im=Image.open(target)
record={'schemaVersion':1,'assetId':'lanxian_spring','tile':'r08_c10','role':'regional_structure_reference_only_not_final_art','file':str(target),'sha256':sha(target),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'route':'builtin','tool':'image_gen.imagegen','generatedAt':meta['completedAt'],'recordedAt':datetime.now(timezone.utc).isoformat(),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['path'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in tool exposes no model/quality selector and returned no verifiable model or quality.','references':refs,'prompt':str(base/'prompt.txt'),'toolResultMetadata':meta,'originalToolResultImagePath':str(source),'originalToolResultImageSha256':sha(source),'qa':{'status':'layout_only_native_detail_pending','acceptedFinalArt':False,'macroGeometry':'tree/planter and railing positions retained; fine floor geometry reconstructed and requires edge review','westStripJoin':'visible guide strip at x approximately70; not suitable for final pixels; native reconstruction must join exact c09 overlap','crossAppearanceAlignmentAccepted':False}}
(base/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(target),'size':im.size,'sha256':sha(target)},ensure_ascii=False))
