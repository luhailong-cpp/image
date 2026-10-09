from pathlib import Path
import json,sys
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(O));import ai_helper as h
axis=sys.argv[1];state=json.loads((O/sys.argv[2]).read_text(encoding='utf8'));c=state['current'];selfim=Image.open(c['r11_c14']).convert('RGB')
if axis=='north':
 neighbor='r10_c14';im=Image.new('RGB',(4096,1254));im.paste(Image.open(c[neighbor]).crop((0,3469,4096,4096)),(0,0));im.paste(selfim.crop((0,0,4096,627)),(0,627))
else:
 neighbor='r11_c13' if axis=='west' else 'r11_c15';im=Image.new('RGB',(1254,4096))
 if axis=='west':im.paste(Image.open(c[neighbor]).crop((3469,0,4096,4096)),(0,0));im.paste(selfim.crop((0,0,627,4096)),(627,0))
 else:im.paste(selfim.crop((3469,0,4096,4096)),(0,0));im.paste(Image.open(c[neighbor]).crop((0,0,627,4096)),(627,0))
joint=O/(axis+'-joint-source.png');im.save(joint);h.derived(joint,[Path(c[neighbor]),Path(c['r11_c14'])],{'method':'native joint627+627 no resize','axis':axis})
prompts={
'north':[
'This part contains vivid turquoise sea. Remove the horizontal artificial division at y627 and the115px inherited guide strip below it (to y742). Continue the same irregular wave cells and foam trails through it. The left557px are a protected, already corrected four-tile corner: preserve them precisely, and smoothly reconnect from x557 to the rest.',
'This part may contain sail spars and water. Remove the horizontal artificial division at y627 and inherited guide palette strip to y742. Continue any existing straight golden wooden spars, ropes, cream fabric and wave contours across it without adding or removing joints.',
'This part may contain ivory sail, golden spars, pier timber and water. Remove the horizontal artificial division at y627 and guide strip to y742. Reconnect every existing diagonal timber contour, highlight, rope and real structural joint exactly. Preserve original object count, perspective and locations.',
'This part contains timber pier planks, posts, rope rail and turquoise sea. Remove the horizontal artificial division at y627 and guide strip to y742. Continue the same plank gaps and chamfer highlights through it without new joints. The right557px are a protected corrected corner: preserve them, smoothly reconnecting to the rest from x697.'],
'west':[
'Remove the artificial vertical division at x627 and inherited guide strip to x742 through turquoise sea; connect existing waves and any timber contours. Top557px are a protected corrected corner; preserve them, blending the exact old wave positions into the repaired edge below y557.',
'Remove the artificial vertical division at x627 and inherited guide strip to x742. Continue the existing dock or boat timbers and turquoise waves with identical thickness, direction and warm light. Preserve all real joints.',
'Remove the artificial vertical division at x627 and inherited guide strip to x742. Continue existing boat gunwale, planks, bevel edges and waves without steps, doubled lines, invented plank joints or added objects.',
'Remove the artificial vertical division at x627 and inherited guide strip to x742. Continue the existing boat/deck contours, bevel edges and wave shapes. Keep every real plank seam and rope.'],
'east':[
'Remove the artificial vertical division at x627 and any straight inherited palette strip. Continue the same pier planks, rope rails and turquoise sea. Top557px are a protected corrected corner; preserve them, reconnecting below y557.',
'Remove the artificial vertical division at x627. Continue the same sea waves, foam, rope and existing boat/wood contours exactly through it, removing all rectangular palette strips.',
'Remove the artificial vertical division at x627. Continue the same irregular sea wave cells and foam through it. Preserve any existing sail/boat outlines and ropes.',
'Remove the artificial vertical division at x627. Continue the same sea wave cells, foam and existing wood/boat contours through it. Preserve all real rope and structural joints.']}
spec=[]
for i,z in enumerate([0,1024,2048,2842]):
 n=axis+'-'+str(i+1);box=(z,0,z+1254,1254) if axis=='north' else (0,z,1254,z+1254);p=O/(n+'-source.png');im.crop(box).save(p);h.derived(p,[joint],{'method':'exact native1254 crop','bbox':box,'noResampling':True})
 prompt='Use case: precise-object-edit. Reference1 is the exact native1254x1254 target. '+prompts[axis][i]+' Work across the central seam and reconnect smoothly to the original contours outside that band. Preserve exact camera, object scale, composition and all real construction joints. Reference2 is the approved style only: bright clean rounded Taoist Q-game handpainted finish. No UI/text, extra waves, objects, global recoloring, blur, warp or rescale. Output exactly1254x1254.'
 h.savecall(n,prompt,[p,h.STYLE],['exact native repair target','actual approved04guild style']);spec.append({'name':n,'offset':z,'source':str(p)})
(O/(axis+'-spec.json')).write_text(json.dumps({'axis':axis,'neighbor':neighbor,'inputState':sys.argv[2],'joint':str(joint),'patches':spec},indent=2),encoding='utf8');print(axis+' prepared')

