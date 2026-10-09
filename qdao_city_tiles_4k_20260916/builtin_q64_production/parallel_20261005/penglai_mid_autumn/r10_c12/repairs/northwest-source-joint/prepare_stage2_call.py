from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;v=D/"stage2-active"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
prompt="""Use case: precise-object-edit, local water lighting continuity.
Edit Image1, the exact native1254x1254 water-and-stone crop. Preserve its entire composition, blue wall, column, reflection, wave pattern, cell shapes, and all stroke widths. The TOP627 rows are finished true northern artwork and must remain unchanged.
At y627 across the middle-left water there is an erroneous straight collage boundary: the same broad blue water cells abruptly become darker below the line. Heal ONLY this lower-side contact and its tiny wave-edge interruptions, mainly x128..968 below y627, continuing the exact existing upper wave contours and colors smoothly downward. Preserve the large water cells and the warm reflection's exact location. Keep the already connected far-left overlap, right stone wall, and all surrounding finished regions unchanged. Subtly return to the existing lower water by y920; keep the bottom330 rows. Do not preserve the wrong straight shade cut merely because it is present in the input.
Image2 is approved art STYLE only. Use Image1 as sole geometry authority: clean cobalt-blue water with simple broad softly painted cyan curves and its existing warm pale reflected light. No new foam, glints, glitter, cells, objects, sharpening halos, grain, blur, daylight relighting, text, border, zoom, crop, resize or rotation. Return one opaque1254 square in the identical frame."""
refs=[v/"context.png",Path("D:/work/image/designs/gameplay-ui/04-guild.png")];call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
(v/"actual.prompt.txt").write_text(prompt,encoding="utf-8");write(v/"actual.call.json",call)
req=dict(preparedAt=datetime.now(timezone.utc).isoformat(),configSnapshot=read(D/"root-v1.request.json")["configSnapshot"],submittedParameters=dict(model=None,quality=None,**call),actualSubmitted=call,prompt=str(v/"actual.prompt.txt"),promptSha256=sha(v/"actual.prompt.txt"),references=[ref(p) for p in refs],mapping=ref(v/"mapping.json"),sourceStage1=ref(D/"stage1-bounded/r10_c12-proposal.png"),actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin exposes no model/quality selectors or response evidence.",approvedForPromotion=False)
write(v/"actual.request.json",req);print(str(v/"actual.call.json"))

