from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
from datetime import datetime,timezone
H=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
src=Path('C:/Users/luyua/.codex/generated_images/01a10ba8-a0c3-7813-b821-7603374ed7c1/exec-1e4a98b7-bb90-4e73-ac12-dbf7922e6b8b.png')
dst=H/'attempt1.png';shutil.copyfile(src,dst);im=Image.open(dst);assert im.size==(1254,1254)
call=read(H/'call.json')
write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=datetime.now(timezone.utc).isoformat(),width=im.width,height=im.height,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=call['configSnapshot'],submittedParameters=call['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin tool exposes no model/quality selectors or response metadata.',prompt=str(H/'prompt.txt'),references=call['references'],evidence=dict(toolOutputPath=str(src),toolOutputSha256=sha(src)),status='rejected_wrong_left_geometry',rejectionReason='Image straightened the immutable left paving toward the incorrect right context; left shared endpoint drift is about70px, beyond native registration allowance. Not merged.'))
mask=Image.new('L',(1254,1254),0);d=ImageDraw.Draw(mask)
# This is only an inpainting mask, never artwork. Protect a broad halo around the existing rail.
polygon=[(627,170),(1135,170),(1135,1050),(1008,1050),(1008,786),(944,748),(744,748),(666,794),(666,1040),(627,1040)]
d.polygon(polygon,fill=255);mask.save(H/'edit-mask.png')
target=Image.open(H/'target.png').convert('RGB');blank=Image.new('RGB',target.size,(255,255,255));masked=Image.composite(blank,target,mask);masked.save(H/'masked-target.png')
prompt='''Use case: precise-object-edit / inpaint missing pavement. Output one native1254×1254 image.
Image1 is our bright clean rounded fantasy-game STYLE reference only. Image2 is the EDIT TARGET with a white missing-pavement region. Image3 is its binary mask: white pixels need AI painting, black pixels are immutable. Fill ONLY the white missing region. White is not pavement; it marks missing artwork. Preserve every already-painted pixel outside that white region, especially the ENTIRE left627px, exactly in place. No camera, scale, tile-size or perspective change. Do not straighten or move any left-side grout to accommodate the right side.

Reconstruct the missing purple-blue stone floor so all visible existing grout endpoints on the mask boundary connect naturally. The authoritative left diagonal grout enters the hole at x627,y410; extend that exact endpoint into the new painting. The lower left stone face is plain at x627,y874 and must stay plain across the boundary: DO NOT introduce an orphan diagonal seam there. The existing lower descending seam passes x627,y952; keep it in place. The large old-left stone grid is correct. Match it. Preserve the rounded blue stone rail/post and its painted halo at the lower right.

Use crisp dark grout and thin warm edge highlights; softly rounded clean stone volumes, smooth broad purple-blue painted color with restrained warm sunlight. Rebuild a coherent believable floor-tile arrangement in the hole without duplicate stubs, disconnected lines, arbitrary vertical cuts, stretched blurs, cracks or noise. No added objects, text, decoration, steps, changed road layout, or altered railing. This is local native repair of missing connections, not a redesign. Preserve all already-painted content outside the white mask; only the white hole is paintable.'''
(H/'retry-prompt.txt').write_text(prompt,encoding='utf-8')
refs=[call['references'][0],dict(file=str(H/'masked-target.png'),sha256=sha(H/'masked-target.png'),role='edit_target_with_white_inpainting_hole'),dict(file=str(H/'edit-mask.png'),sha256=sha(H/'edit-mask.png'),role='binary_editability_mask_white_edit_black_preserve')]
write(H/'retry-call.json',dict(preparedAt=datetime.now(timezone.utc).isoformat(),tool='image_gen.imagegen',route='builtin',configSnapshot=call['configSnapshot'],submittedParameters=dict(model=None,quality=None),actualModel=None,actualQuality=None,promptFile=str(H/'retry-prompt.txt'),references=refs,source=call['source'],maskPolygon=polygon,maskOnlyPreparation=True,artworkWasNotPaintedByCode=True,outputPending=True))
print('saved attempt1 provenance; prepared masked retry')
