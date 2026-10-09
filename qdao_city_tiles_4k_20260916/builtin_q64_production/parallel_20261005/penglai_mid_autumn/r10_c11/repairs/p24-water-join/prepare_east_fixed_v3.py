from pathlib import Path
from PIL import Image
import json,hashlib,datetime
D=Path(__file__).resolve().parent/'east-fixed-v3';D.mkdir(exist_ok=True);assert not any(D.iterdir())
T=D.parents[2];R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(T/'plan.json');prior=D.parent/'east-centered-v2/host-result.png';east=Path(plan['eastCandidate']);style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
assert sha(east)==plan['eastCandidateSha256']
im=Image.open(prior).convert('RGBA');im.paste(Image.open(east).convert('RGBA').crop((0,909,627,2163)),(627,0))
context=D/'context.png';im.save(context)
sources=[ref(prior),ref(east)]
mapping=dict(globalFrameXYWH=[44429,37773,1254,1254],trueEastBoundaryX=627,operations=[dict(source=str(prior),cropLTRB=[0,0,627,1254],pasteXY=[0,0]),dict(source=str(east),cropLTRB=[0,909,627,2163],pasteXY=[627,0])],holeLTRB=[420,0,627,1254],candidatePasteLeft627ToP24X512=True,sourceUpscaling=False,realEastPixelsNotMasked=True)
write(str(context)+'.generation.json',dict(**ref(context),derivedFrom=sources,operation=mapping,actualModel=None,actualQuality=None,nativeScale=1,approvedForPromotion=False))
im.paste((0,0,0,0),(420,0,627,1254));target=D/'target.png';im.save(target)
write(str(target)+'.generation.json',dict(**ref(target),derivedFrom=[ref(context)],operation=dict(clearRGBAHoleLTRB=[420,0,627,1254],allOtherPixelsUnchanged=True),actualModel=None,actualQuality=None,nativeScale=1,approvedForPromotion=False))
prompt='''Use case: precise-object-edit. Fill ONLY the transparent vertical gap of Image1, which is x420 through626 in this exact1254x1254 crop. The entire visible RIGHT half x627..1253 is immutable finished artwork: keep its original colors, exact shapes, and brushwork, without brightening, darkening, hue shifting or repainting it. This is green tree foliage beside cobalt water. Match the exact local color on the RIGHT edge of the gap first, then continue those same visible partial leaves leftward into the fixed existing leaves at x419. Each cut leaf on the right must become one coherent complete leaf with its precise outline, vein, highlight and shadow continuing across x627 with no straight color or geometry edge. Do not create half bright/half dark leaves, extra leaf clusters, flower centers, straight vertical seams, or abrupt blue water bands. The water at the top must connect the existing wave shapes smoothly through the gap. Preserve the foliage silhouette and clipped branch. Image2 is the unmasked context at the same physical frame: use only for positions, while its former join at x627 is a defect to eliminate. Image3 supplies approved clean bright rounded Daoist chibi painting STYLE only; import no UI/text/objects. Keep the same crop, scale, camera, lighting, jade/dark green and gold leaves, and vivid cobalt water. No blur, glow, noise, rotation, mirroring or zoom. Return fully opaque1254x1254. Preserve all already-visible areas of Image1 exactly; only paint missing pixels.'''
pp=D/'repair.prompt.txt';pp.write_text(prompt,encoding='utf8')
refs=[dict(**ref(target),role='exact1254 native edit target, only current-side narrow corridor transparent; true E entirely visible'),dict(**ref(context),role='same-frame unmasked source geometry; old vertical join defective'),dict(**ref(style),role='approved hand-painted style')]
call=dict(prompt=prompt,referenced_image_paths=[x['file'] for x in refs],transparent_background=False)
write(D/'repair.call.json',call)
write(D/'repair.request.json',dict(preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=ref(context),sources=sources,sourceGeneration=ref(str(prior)+'.generation.json'),plan=ref(T/'plan.json'),prompt=ref(pp),references=refs,mapping=mapping,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read(Path('D:/work/image/config/image-generation.json')),actualModel=None,actualQuality=None,canonicalUnchanged=True))
print(target)
