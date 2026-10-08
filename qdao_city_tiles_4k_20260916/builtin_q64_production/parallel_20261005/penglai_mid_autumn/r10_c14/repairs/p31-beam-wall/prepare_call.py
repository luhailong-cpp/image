from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
source=D/"input-original.png"
im=Image.open(source).convert("RGBA")
poly=[(552,515),(590,489),(625,472),(660,475),(670,572),(623,629),(553,661)]
mask=Image.new("L",im.size,0);ImageDraw.Draw(mask).polygon(poly,fill=255)
mask.save(D/"replacement-mask.png")
alpha=Image.new("L",im.size,255);alpha.paste(0,(0,0),mask);im.putalpha(alpha)
target=D/"edit-target.png";im.save(target)
prompt="""Use case: precise-object-edit.
Image 1 is the EDIT TARGET: a native-scale 1254 by 1254 crop of our finished game-map candidate. The small transparent hole immediately behind the large center-left round timber post removes an erroneous short semi-transparent wooden beam that penetrated the masonry. Fill only this small hole with the continuous blue-purple stone wall that should be behind the post. Restore the existing vertical dark masonry joint coming down from above through this hole until it meets the existing diagonal dock edge, using the same broad clean stone brushwork, lighting and colors as the surrounding wall. There must be no wood, golden stripe, ghost beam, ledge, new stone subdivisions or paint haze inside the wall repair. The correct left wooden rail ends naturally at the large post; no rail continues behind the post into the wall.
Image 2 is the unmasked BEFORE crop, a geometry reference only: the faded short wooden segment on the post's right is the defect to REMOVE, not reference geometry to reproduce.
Image 3 is the approved artwork style reference for the bright, clean, round Q-style hand-painted material finish; do not import any UI content or objects.
Keep the entire 1254 by 1254 camera frame and every opaque pixel as unchanged as possible. Preserve the exact silhouette and highlight of the large round post, the wooden beam arriving from the left, the front diagonal railing, all dock planks, rope post, water, wall outlines and all other objects. No rescaling, viewpoint change, new objects, new borders or additional small outlined masonry tiles. Fill the transparent repair hole completely with opaque finished stone. Output the complete same-size fully opaque repaired scene."""
(D/"prompt.txt").write_text(prompt,encoding="utf-8")
refs=[str(target),str(source),"D:/work/image/designs/gameplay-ui/04-guild.png"]
call=dict(prompt=prompt,referenced_image_paths=refs,transparent_background=False)
write(D/"call.json",call)
config=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8"))
write(D/"request.json",dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),tool="image_gen.imagegen",route="builtin",configSnapshot=config,submittedParameters=dict(model=None,quality=None),actualSubmitted=call,prompt=dict(file=str(D/"prompt.txt"),sha256=sha(D/"prompt.txt")),actualSubmittedPromptSHA256=hashlib.sha256(prompt.encode()).hexdigest(),references=[dict(file=r,sha256=sha(r),role=("edit target","before geometry: erroneous transparent beam must be removed","approved style reference")[i]) for i,r in enumerate(refs)],actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin; model and quality selectors are not exposed."))
m=json.loads((D/"mapping.json").read_text());m.update(localRepairPolygon=poly,globalRepairPolygon=[[x+256,y+2250] for x,y in poly],replacementMask=dict(file=str(D/"replacement-mask.png"),sha256=sha(D/"replacement-mask.png")),editTarget=dict(file=str(target),sha256=sha(target)),operation="Crop/mask preparation only; AI must paint the missing wall. Proposal composite copies only the exact mask pixels from the returned same-frame host.");write(D/"mapping.json",m)
write(D/"edit-target.png.generation.json",dict(file=str(target),sha256=sha(target),derivedFrom=[dict(file=str(source),sha256=sha(source))],operation="Alpha hole in exact repair polygon; no art painted by code.",replacementMask=m["replacementMask"]))
print(json.dumps(call))

