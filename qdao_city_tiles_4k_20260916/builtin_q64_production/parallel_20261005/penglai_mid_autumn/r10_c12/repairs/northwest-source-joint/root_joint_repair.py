"""Native source-corner AI repair request and literal output provenance only."""
from pathlib import Path
import sys,shutil
F=Path(__file__).resolve().parent;ROOT=F.parents[2];sys.path.insert(0,str(ROOT))
from production import read,write,sha,now,REPO
from PIL import Image
P='root-v1'
def prepare():
    target=F/'four-quadrant-context1254.png';style=REPO/'designs/gameplay-ui/04-guild.png'
    prompt='''Use case: precise-object-edit, seamless water lighting repair. Edit Image1, an EXACT native1254x1254 crop of a continuous painted game-map water surface. Preserve the entire composition, camera, wave pattern, shapes, positions and stroke widths. Return one opaque1254 square at exactly the same framing.
Image1 is the sole composition and exact-pixel geometry authority. The TOP627 rows are already correct: preserve them. At y627 there is an erroneous ruler-straight horizontal collage boundary; the water immediately below is abruptly darker and the blue tones jump. Repair ONLY the lower-side water colors and the few tiny wave-edge interruptions at that horizontal line, making the already painted waves continue naturally from the upper half. Maintain the underlying curving cyan wave paths, their exact entry/exit locations, and all warm pale reflections in the lower-right. Preserve each existing wave cell instead of inventing a new water pattern. The lower-left and lower-right are one continuous water surface, not separate images. There must be no horizontal ledge, broad straight band, grid, square patch or vertical join at x627. Subtly settle back into the original lower water by y920; retain the bottom330 rows and all outer composition. Do not flatten the intentional broad water brushwork or change the nighttime lighting into daylight.
Image2 is the approved art STYLE only: bright, clean, rounded Daoist chibi hand painting with restrained organized brushwork. Do not copy any UI, text, buildings, objects or characters. Keep Image1's clear cobalt blue water, flowing light-blue strokes and existing warm light reflections. No sky, horizon, moon, new objects, glitter, grain, blur, sharpening halos, extra tiny ripples, text or border. This is a local lighting-continuity repair at original resolution, not a redesign.'''
    pp=F/(P+'.prompt.txt');assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
    call=dict(prompt=prompt,referenced_image_paths=[str(target),str(style)],transparent_background=False)
    write(F/(P+'.call.json'),call)
    write(F/(P+'.request.json'),dict(preparedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(file=str(p),sha256=sha(p),role=role) for p,role in [(target,'exact native four-quadrant edit target'),(style,'approved primary art style')]],mapping=dict(file=str(F/'mapping.json'),sha256=sha(F/'mapping.json')),actualModel=None,actualQuality=None))
    print(str(F/(P+'.call.json')))
def save(src):
    src=Path(src);dst=F/(P+'.png');req=read(F/(P+'.request.json'));assert not dst.exists();assert Image.open(src).size==(1254,1254)
    for v in req['references']:assert sha(v['file'])==v['sha256']
    shutil.copy2(src,dst);write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin; no exposed selectors or returned actual model/quality evidence.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],mapping=req['mapping'],sourceUpscaled=False,resizedAfterGeneration=False,canonicalImagesChanged=False,accepted=False))
    print(str(dst));print(sha(dst))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='save':save(sys.argv[2])
