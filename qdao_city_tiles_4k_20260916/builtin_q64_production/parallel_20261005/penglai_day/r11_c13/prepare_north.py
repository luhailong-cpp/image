import helper as h
from PIL import Image,ImageDraw
import numpy as np
R=h.ROOT;p=h.p;D=R/'repairs/north';D.mkdir(parents=True,exist_ok=True)
s=p.read(R/'evidence/boundary-state.json')['north'];assert p.sha(s['source'])==s['sha256'];south=R/'repairs/internal/r11_c13-internal-candidate-v1.png'
base=np.concatenate([np.asarray(Image.open(s['source']).convert('RGB'))[3469:],np.asarray(Image.open(south).convert('RGB'))[:627]],axis=0)
f=D/'north-input.png';Image.fromarray(base).save(f);p.derived(f,[s['source'],south],{'method':'native crop 627px each side; no scaling','globalOriginXY':[49152,40333],'seamY':627})
scenes=['The blue canopy and its same white stripe segments should continue across y627. Join wood frame outlines and remove guide-paste color bands, with no new roof stitches or canvas stripes.','Continue blue canopy edge and timber supports/rail at y627; keep existing cream paving bevels and the exact same plank divisions. Repair only the artificial crossing.','Continue existing timber crate edges, barrel contour, upright and gray quay stone across y627. Preserve exact object dimensions and contour endpoints, no new crates or barrel hoops.','Continue gray quay wall and its timber fender post across y627, and make turquoise water foam and pigment continuous. No extra foam, piles or wall joints.']
jobs=[]
for i,x in enumerate([0,1024,2048,2842],1):
    n=f'n{i}';f=R/'references'/f'{n}-input.png';Image.fromarray(base[:,x:x+1254]).save(f);p.derived(f,[D/'north-input.png'],{'method':'native integer crop','boxLTRB':[x,0,x+1254,1254]})
    prompt='Use case: precise native shared-edge inpainting. Image1 is a1254-square true-scale crop of two adjacent Taoist Q game-map tiles with an ARTIFICIAL horizontal join y627. Image2 is approved PRIMARY bright clean rounded handpainted style only. '+scenes[i-1]+' Repair the mismatch at y627 so all original geometry is one continuous coherent scene. Keep top/bottom160px and left/right edge endpoints fixed. Same crop, camera, scale, colors and object count; no new objects, lines, UI or text. Output1254x1254.'
    call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),h.STYLE],'transparent_background':False};h.savecall(n,call);jobs.append({'name':n,'startX':x,'input':str(f)})
p.write(D/'state.json',{'north':s,'southTop627Source':str(south),'southSha256':p.sha(south),'jobs':jobs,'globalOriginXY':[49152,40333],'formalAccepted':False})
f=R/'references/i2-tiny-input.png';im=Image.open(R/'native/i2.png').convert('RGB');ImageDraw.Draw(im).rectangle((655,584,691,654),fill=(255,0,255));im.save(f);p.derived(f,[R/'native/i2.png'],{'method':'magenta editing guide marks defective notch only; not final art','boxLTRB':[655,584,692,655]})
prompt='Use case: tiny inpainting. Image1 is the exact target. Replace ONLY the magenta rectangular hole near x670,y619 with a continuous smooth right edge of the existing orange wooden crate upright. The dark vertical outline must connect from above to below with no horizontal step, no notch and unchanged post width. Fill wood on the left and cream paving on right exactly matching surrounding pixels. Leave every other part pixel-identical including shadows, stone and wood edges. Image2 approved PRIMARY style only. No magenta remains. Same1254-square crop.'
h.savecall('i2-tiny',{'prompt':prompt,'referenced_image_paths':[f.as_posix(),h.STYLE],'transparent_background':False})
print('Prepared4 north native crops and tiny notch target')
