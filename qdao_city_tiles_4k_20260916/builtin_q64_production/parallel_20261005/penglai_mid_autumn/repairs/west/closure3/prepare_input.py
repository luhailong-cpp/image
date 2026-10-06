from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=Path('D:/work/image');OUT=ROOT/'output/r09_c13'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(OUT/'manifest.json');old=Path(m['westSource']);cur=OUT/'r09_c13.png'
assert sha(cur)=='4adf1d95a12781e56d683977809d555cd018b4621b5b4977afa89c187702c200'
a=Image.open(old).convert('RGB');b=Image.open(cur).convert('RGB')
im=Image.new('RGB',(1254,1254));im.paste(a.crop((3469,1894,4096,3148)),(0,0));im.paste(b.crop((0,1894,627,3148)),(627,0));target=HERE/'target.png';im.save(target)
prompt='''Use case: precise-object-edit. Edit Image2, the native1254×1254 paving repair target. Image1 is only the established bright clean rounded Chinese fantasy game painting/style reference; do not copy UI or objects from Image1. Output exactly1254×1254 native pixels, no scaling.

This target intentionally contains a BROKEN vertical join at x627. The left627px is the immutable old neighboring tile; preserve its paving, lines, color, texture and contours exactly. The right627px is the newer tile. Repair only the right-side paving within x627..1127 and y180..1060. Leave the outer100px boundary and the stone railing/pillar below unchanged. Do not redesign the layout or add decorative objects.

Two specific structural problems require actual new painted connections, not blur or color camouflage:
1. At the join, the existing old LEFT diagonal grout center is at image y410 (world/local tiley2304). The right diagonal grout incorrectly meets the join at image y338 (tiley2232),72px too high. Redraw the right-side paving geometry so the old left seam/highlight crosses x627 continuously at exactly its existing y410 and naturally meets the established right-side paving beyond x1127. Reconstruct clean coherent rounded stone tile contours. Do not move the old left endpoint upward. Do not keep two disconnected stubs.
2. At x627,image y874 (tiley2768), a right-side ascending diagonal seam starts abruptly against a plain old-left stone face. Remove/rebuild this orphan seam inside the editable right-side area and connect the paving coherently to the existing lower diagonal seam at image y952 (tiley2846) and the fixed right context. The old-left plain paving here is correct and must remain plain. Do not invent a seam on the left to justify the right error.

Preserve the already-continuous lower diagonal at tiley2846..2848 and the rounded stone railing. Same bright clean soft volumetric purple-blue stone, restrained warm light, crisp smooth dark grout with thin warm highlights, no dirty cracks, noise, blur, duplicate lines, abrupt vertical cut, new stairs or changed building/road footprint. Make the drawing genuinely continuous across x627. The left half is exact structural evidence, not an approximate style suggestion.'''
(HERE/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[dict(file=str(PROJECT/'designs/gameplay-ui/04-guild.png'),sha256=sha(PROJECT/'designs/gameplay-ui/04-guild.png'),role='style_reference'),dict(file=str(target),sha256=sha(target),role='edit_target_original_pixels_with_broken_join')]
write(HERE/'call.json',dict(preparedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=read(PROJECT/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,promptFile=str(HERE/'prompt.txt'),references=refs,source=[dict(file=str(old),sha256=sha(old),cropLTRB=[3469,1894,4096,3148]),dict(file=str(cur),sha256=sha(cur),cropLTRB=[0,1894,627,3148])],nativeInputPixels=[1254,1254],outputPending=True))
print(str(target))
