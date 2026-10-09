"""Prepare and preserve a same-frame built-in edit; no AI call or image scaling."""
from pathlib import Path
import sys, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from production import REPO,read,write,sha,now
F=ROOT/'r09_c15';R=F/'references';BASE=F/'night-water-fix'
def prepare():
    assert not BASE.with_suffix('.request.json').exists()
    refs=[R/'structure.png',ROOT.parent/'penglai_day/r09_c15/references/structure.png',R/'west-preview.png',REPO/'designs/gameplay-ui/04-guild.png']
    prompt='''Use case: precise-object-edit. Image1 is the edit target. Correct ONLY the WATER BACKGROUND of this continuous isometric top-down game-map crop. The invented moon, sky, clouds, stars and distant horizontal horizon across its upper150px are wrong: remove all of them and replace that area with the same harbor WATER SURFACE extending upward out of the crop. This view is entirely looking down onto water and land; no sky or horizon is visible anywhere. Match Image2's water-only background geometry and wave flow, translated into the current luminous cobalt-blue NIGHT palette. Simplify the rest of the water into broad clean hand-painted cyan wave ribbons and calm cobalt areas like Image2, removing the narrow glittery vertical moon-reflection stripe and noisy photographic ripples. Keep readable night water, not cyan daylight.
Image2 supplies the exact shared daylight map geometry and water composition only. Image3 is the actual WEST NIGHT neighbor, supplying blue-violet rock, jade foliage and honey-gold wood colors; only its rightmost edge touches Image1's leftmost edge. Image4 is the approved bright, rounded Daoist chibi painted art style only; copy no UI or text.
Preserve Image1's exact1254x1254 frame, camera, scale, all rock silhouettes and occupied footprints, plant positions, fence slope, post counts and positions, ropes, coral and ivory cloth panels, paving, cropped foreground timber and square stone bollard. Preserve the SINGLE EXISTING warm lantern with its red-brown stand and rounded jade base at lower center-left exactly as shown in Image1; it belongs to the night map, even though absent in Image2. Keep all cropped objects cropped. Do not add, move or redesign anything. Do not add moon, sky, cloud, horizon, text, border, watermarks, boats, extra lights or decorative objects. Make only the water correction. Return one opaque1254x1254 full-frame image with the same composition.'''
    pp=BASE.with_suffix('.prompt.txt');pp.write_text(prompt,encoding='utf-8')
    call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(BASE.with_suffix('.call.json'),call)
    write(BASE.with_suffix('.request.json'),dict(preparedAt=now(),configSnapshot=read(F/'night-structure.request.json')['configSnapshot'],submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p),role=role) for p,role in zip(refs,['edit target, rejected sky/water only','shared water geometry, read-only','actual W night colors and boundary','approved style'])],planningFrameGlobalXYWH=[57229,32653,4326,4326],productionPixels=False,formalAccepted=False))
    print(str(BASE.with_suffix('.call.json')))
def save(source):
    req=read(BASE.with_suffix('.request.json'));src=Path(source);dst=R/'structure-water-fixed.png'
    assert not dst.exists() and Image.open(src).size==(1254,1254)
    for r in req['references']:assert sha(r['file'])==r['sha256']
    shutil.copy2(src,dst)
    write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed built-in exposes and returns no model or quality selectors.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],planningFrameGlobalXYWH=req['planningFrameGlobalXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,formalAccepted=False))
    print(str(dst));print(sha(dst))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='save':save(sys.argv[2])
