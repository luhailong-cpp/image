from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
T=Path(__file__).resolve().parent.parent;R=T/'repairs/east-ledge-20261016-v1';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
I=read(T/'repairs/blind-grout-20261016-v1/manifest.json')
write(T/'repairs/blind-grout-20261016-v1/I01.quickqa.json',{'status':'local_geometry_pass','native':I['native'],'candidate':I['candidate'],'observation':'False vertical groove erased; true horizontal course preserved; narrow mask texture join visually coherent; all four384edges byte-identical. Not whole-art acceptance.','formalAccepted':False})
P=read(T/'progress.json');P.update(candidate=I['candidate']['path'],context=I['context']['path'],localRepairManifest=str(T/'repairs/blind-grout-20261016-v1/manifest.json'),activeNativeRepairCount=1,actualNativeOutputCount=20,internalArtQA='pending_material_review',status='candidate_local_geometry_review_complete_east_repair_pending',updatedAt=datetime.now(timezone.utc).isoformat(),nextStep='East ledge retry; north pair awaits actual adjacent core; retain material/red fragment pending.');write(T/'progress.json',P)
write(R/'E01.quickqa.json',{'status':'rejected_preserved','actualModel':None,'nativeSha256':sha(R/'E01-native.png'),'reason':'Right locked reference ledge moved upward toward left rather than correcting this tile down to actual neighbor. Cannot composite and call seam fixed.'})
prep=read(R/'preparation.json');base=Image.open(I['candidate']['path']).convert('RGB');east=Image.open(prep['east']['path']).convert('RGB')
target=R/'E02-target.png';im=Image.new('RGB',(1254,1254));im.paste(base.crop((3468,0,4096,1254)),(0,0));im.paste(east.crop((0,0,626,1254)),(628,0));im.save(target)
req=read(R/'E01.request.json');req['referenced_image_paths'][-1]=str(target)
req['prompt']='Use case: precise-object-edit. Fix ONE 7px mismatch in the exact native image4 LAST, output1254x1254. Images1/2/3 style only. In image4, vertical boundary x628 splits LEFT this tile from RIGHT locked neighbor. RIGHT x628..1254 is immutable: its horizontal ledge REAR edge is at y347 and its FRONT highlight is at y373. LEFT currently has rear edge at y339 and front highlight y365, 8pixels too high. Lower ONLY LEFT ledge upper surface in x250..628 to meet RIGHT original y347 and y373 at x628, reconnecting smoothly to unchanged far-left. Do NOT raise the right ledge. This is crucial: leave all pixels RIGHT x628..1254 exactly as supplied. Keep the bottom of the left ledge y458 unchanged. The small left upper-wall face must extend down to the new rear edge. Preserve existing joint at x620 and all framing, texture, color, stone scale, shadows. Change only x250..628,y315..395. All y0..192 and y395..1254 and x0..250 remain unchanged. No new grout, text, UI, objects or decoration; no reconstruction or resize.'
write(R/'E02.request.json',req);write(R/'E02.preparation.json',{'target':str(target),'targetSha256':sha(target),'base':I['candidate'],'baseContext':I['context'],'east':prep['east'],'origin':[3468,0],'status':'prepared_not_generated'})
print(json.dumps(req))

