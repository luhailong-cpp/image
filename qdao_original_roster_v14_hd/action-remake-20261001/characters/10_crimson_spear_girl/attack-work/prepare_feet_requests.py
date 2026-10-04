from pathlib import Path
from PIL import Image
import json
B=Path(__file__).parent;R=B.parent
s=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
shared=["D:/work/image/q_daoist_character_pack_4096/10_crimson_spear_girl_transparent_4096.png","D:/work/image/designs/jubaozhai-ui/02-characters.png"]
queue=[]
for direction in ["E","W"]:
 for n in range(1,13):
  if n==6: continue
  slot=f"attack/{direction}/{n:02d}"; source=R/s[slot];stem=f"attack-{direction}-{n:02d}-feet-v1"
  im=Image.open(source);box=im.getchannel("A").point(lambda v:255 if v>=32 else 0).getbbox()
  toward="RIGHT / EAST" if direction=="E" else "LEFT / WEST"; rear="screenLEFT" if direction=="E" else "screenRIGHT"
  footref=B/("attack-E-06-v4.png" if direction=="E" else "attack-W-06-v3.png")
  moon=R.parent/"07_moon_shadow_assassin_girl"/"frames"/"attack"/direction/"06.png"
  prompt=f"""Use case: precise-object-edit. Edit ONLY the REAR BOOT of image1. One1254x1254 native square transparentRGBA sprite.
Image1 is original attack phase {n:02d}/12. Preserve its exact existing body/head/weapon pixels, scale and absolute canvasposition. Original main silhouette spans y{box[1]} to y{box[3]}; retain these original positions, do not recenter/resize. Do not move either ankle, any knee, the pelvis, head, gun or hands.
Rear boot on {rear} currently points outward towardviewer. Repaint only this boot and the tiny ankle connection so heel-to-toe longaxis points screen{toward}, parallel to frontboot andattack. Clearly SIDE-VIEW heel and toe; no front-facing toe box, no V-shaped duckfoot. Keep heel/forefoot bearing on original groundheight, same redgold/silver bootdesign. Keep wide stance, limb lengths, pose and weightshift; do not narrow orchange legspacing. Front boot stays unchanged if already aligned.
Image2 shows corrected rearboot direction only; copy NO bodyposition, bodypose, or canvasplacement fromimage2. The original phase1 must remainphase1 etc: no replacing everytarget with the reference phase6. Image3 identitydetails, image4 approved paintingstyle. Image5Moon correspondingdirection attack is only footstructurecomparison, not identity/weapon/wholepose; do not copy any outwardrearfoot there. Preserve anatomicalLEFT forward/high grip toward redhead, RIGHT back/low toward goldbutt; one longstraightrigidshaft, bothcompleteends, fingersconnected. No mirror/crop. No scene/floor/shadow/text. Native1254square withrealalpha. Localbootedit only."""
  args={"prompt":prompt,"referenced_image_paths":[str(source).replace("\\","/"),str(footref).replace("\\","/"),*shared,str(moon).replace("\\","/")],"transparent_background":True}
  (B/(stem+".prompt.txt")).write_text(prompt,encoding="utf-8")
  (B/(stem+".request.json")).write_text(json.dumps(args,ensure_ascii=False,indent=2),encoding="utf-8")
  queue.append({"slot":slot,"stem":stem,"previous":s[slot]})
(B/"feet-repair-queue.json").write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding="utf-8")
print(len(queue))

