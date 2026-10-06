from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
H=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
base=json.loads((H/'call.json').read_text(encoding='utf-8-sig'))
polygon=[(627,806),(725,806),(708,819),(694,841),(684,876),(683,920),(627,935)]
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(polygon,fill=255);mask.save(H/'lower-edit-mask.png')
target=Image.open(H/'target.png').convert('RGB');Image.composite(Image.new('RGB',target.size,'white'),target,mask).save(H/'lower-masked-target.png')
prompt='''Use case: precise-object-edit / small inpainting repair. Output exactly1254×1254 native pixels. Image1 supplies only the established bright clean rounded Chinese fantasy-game painting style. Image2 is the edit target. Image3 is its black-and-white editability mask.
Fill ONLY the SMALL WHITE HOLE immediately to the left of the blue rounded stone pillar. This hole represents an erroneous short dark diagonal grout stub that must be REMOVED. Repaint the hole as an UNBROKEN purple-blue stone face continuing directly from the immutable plain stone on the left. No grout, line, ridge, scratch, warm highlight edge, or tile boundary may cross x627 between imagey806 and935. The dark ascending diagonal visible above/right may disappear behind the foreground pillar, but MUST NOT protrude to the pillar's left or start at the old/new join.
Preserve the ENTIRE left627 pixels exactly. Preserve the blue pillar outline/highlights, the correctly connected descending diagonal below imagey950, all other paving and the outer boundary. Do not redesign the grid or fix unrelated parts of this image. The only requested change is filling this small white masked hole with the same continuous smooth purple-blue paving texture as its immediate old-left neighbor. Clean soft rounded stone style, no dirty cracks, no blur, no duplicated lines. Do not paint a replacement seam in this hole. No new objects, text or decoration.'''
(H/'lower-prompt.txt').write_text(prompt,encoding='utf-8')
refs=[base['references'][0],dict(file=str(H/'lower-masked-target.png'),sha256=sha(H/'lower-masked-target.png'),role='edit_target_with_white_hole_over_orphan_grout_stub'),dict(file=str(H/'lower-edit-mask.png'),sha256=sha(H/'lower-edit-mask.png'),role='binary_editability_mask_white_edit_black_preserve')]
write(H/'lower-call.json',dict(preparedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=base['configSnapshot'],submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,promptFile=str(H/'lower-prompt.txt'),references=refs,source=base['source'],maskPolygon=polygon,maskOnlyPreparation=True,artworkWasNotPaintedByCode=True,outputPending=True))
