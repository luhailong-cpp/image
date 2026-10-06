from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
REPO=Path('D:/work/image')
A=ROOT/'r08_c09/repairs/join-endpoint/candidate_4096.png'
B=ROOT/'r08_c10/spring-edits/southwest/candidate_4096.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(A)=='eacc709f26e6224c3b24e493bb4a3a60b8eb44cda18afa787e208f5a1805ff38'
assert sha(B)=='33b86f2d308dfa30a4fe71ec4e219bdf3615a7ab161946bc847649a64eac28f9'
shutil.copyfile(B,OUT/'source-core4096.png')
assert sha(B)==sha(OUT/'source-core4096.png')
a=Image.open(A).convert('RGB');b=Image.open(OUT/'source-core4096.png').convert('RGB')
context=Image.new('RGB',(1254,1254));context.paste(a.crop((3469,700,4096,1954)),(0,0));context.paste(b.crop((0,700,627,1954)),(627,0))
target=OUT/'edit-target-1254.png';context.save(target)
write(OUT/'edit-target-1254.derived.json',{'file':str(target),'sha256':sha(target),'pixels':[1254,1254],'operation':'Exact native integer crop/paste, no resizing or warp; QA/edit context only','worldContextC10LTRB':[-627,700,627,1954],'joinXInContext':627,'sources':[{'file':str(A),'sha256':sha(A),'crop':[3469,700,4096,1954],'placement':[0,0]},{'file':str(B),'sha256':sha(B),'crop':[0,700,627,1954],'placement':[627,0]}]})
prompt=('Use case: precise-object-edit. Image 1 is an exact-native 1254x1254 close-up of an existing game-map stone path, joined vertically at x627. Repair ONLY two very small kinks where the sloping ivory cross-band edges cross that join. The upper dark outline/ivory bevel crosses near (627,483); the lower dark outline/ivory bevel crosses near (627,602). Continue the left-side slopes smoothly into the immediately adjacent RIGHT side with no 2-3 pixel step, doubled line, kink or gap. Keep the left half x0..626 absolutely unchanged. Keep the width, shape, lighting and mapped position of the stone band; adjust only the tiny right-side edge segments, fading naturally back to the existing unchanged routes within x627..827 and y420..680. Preserve ALL other stone joints, curves, surface textures and every pixel outside those two local edge neighborhoods. Do not redraw or recompose the overall scene, enlarge, crop, rotate, sharpen or add objects. No new details, cracks, flowers, symbols, UI or text. Image 2 is ONLY the user-approved primary painting/material reference for clean bright rounded Daoist chibi hand-painted art; copy none of its contents. Return the same opaque full-bleed 1254-square image at identical framing and coordinates, with only the two tiny continuous stone-edge repairs.')
(OUT/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=[{'path':str(target),'role':'Exact native edit target with immutable spring c09 left half and spring c10 southwest right half; only two tiny right-side stone-edge kinks may change'},{'path':str(REPO/'designs/gameplay-ui/04-guild.png'),'role':'User-confirmed primary painting/material reference; no UI, flowers, ornaments or objects copied'}]
write(OUT/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'prompt':str(OUT/'prompt.txt'),'references':refs,'configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['path'] for r in refs]},'sourceC09':{'file':str(A),'sha256':sha(A)},'sourceC10':{'file':str(B),'sha256':sha(B)},'targetContextC10LTRB':[-627,700,627,1954],'allowedC10MaskEnvelope':[0,1120,200,1380]})
print(json.dumps({'target':str(target),'prompt':str(OUT/'prompt.txt'),'request':str(OUT/'request.json')},ensure_ascii=False))
