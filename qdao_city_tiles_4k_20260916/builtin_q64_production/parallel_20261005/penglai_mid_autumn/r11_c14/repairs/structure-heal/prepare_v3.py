from pathlib import Path
import sys,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from heal import now,sha,ref,write,read,derived
R=P.parents[1]/'references'
base=P/'fixed-anchor-base-v2.png';a=np.array(Image.open(base).convert('RGB'));y,x=np.mgrid[:1254,:1254]
# Only blank water at the two true joins. Preserve every boat/sail/post/stone pixel.
hole=((x>=85)&(x<240)&(((y>=85)&(y<610))|((y>=1090)&(y<1254))))|((y>=85)&(y<220)&(x>=85)&(x<465))
rgba=np.concatenate([a,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);rgba[hole]=[255,255,255,0]
target=P/'water-l-edit-target-v3.png';derived(Image.fromarray(rgba),target,[base],dict(kind='AI input only water holes; all physical geometry fixed',waterMaskRegions='x85..240 y85..610 and1090..1254, plus y85..220 x85..465',planningOnly=True))
prompt='''Repair Image 1 ONLY: fill the white transparent missing WATER patches in this exact 1254-square game-map fragment. Return an opaque1254-square with all unmasked content faithfully unchanged. Do not move, replace or repaint the cream sail, mast, posts, boat rim or bench, ropes, short stone wall at far left, or any unmasked water. Image2 is an UNMASKED original for object positions only. Image3 is the actual WEST neighbor to explain water paint scale; Image4 is STYLE ONLY, never UI content.
Critical: the top85 and left85 pixel strips of Image1 are the existing real neighbors. The missing water begins directly to their right/below. Follow each existing small rounded blue ripple and each gold reflection from its actual endpoint at the boundary. Near that boundary the small water cells must stay the SAME size, hue and brightness as the real neighbor, then gradually open into the broader waves of the untouched interior over the width of the hole. Do not draw a separate sheet of large cyan outlined water starting at x85 or y85. Do not add a vertical gold beam at x85. No straight line, sudden hue edge or repetitive straight row of wave highlights may trace the old cut. Flow warm left gold reflections naturally into the adjacent blue water; the current interior is unchanged dark saturated cobalt, not turquoise daylight.
This is NOT a new scene. Preserve EXACT frame, crop, all physical shapes and object counts. Fix ONLY the water gaps. Do not invent a wall extension; the existing short stone wall visible entirely within the left strip already has its shaped terminal edge. Do not remove or redesign the small original boat bow post around x165,y675; it stays intact. Keep polished rounded chibi hand-painted rendering with softly faceted water, restrained gold, and clear clean forms. No photo texture, noise, blur, text, sky, moon, horizon, people or decoration.'''
pp=P/'heal-v3.prompt.txt';pp.write_text(prompt,encoding='utf-8');refs=[target,base,R/'west-context-preview.png',Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
call=dict(prompt=prompt,referenced_image_paths=[str(q) for q in refs],transparent_background=False);write(P/'heal-v3.call.json',call)
write(P/'heal-v3.request.json',dict(preparedAt=now(),notSubmittedYet=True,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read(P/'heal-v2.request.json')['configSnapshot'],references=[ref(q) for q in refs],prompt=ref(pp),base=ref(base),productionPixels=False,nativeDetailCount=0))
write(P/'heal-v1.prepared-only.json',dict(createdAt=now(),request=ref(P/'heal-v1.request.json'),submitted=False,reason='Prepared target included outside-neighbor cyan halo; replaced by v2 before any call.'))
print(P/'heal-v3.call.json')
