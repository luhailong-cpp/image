from pathlib import Path
import sys,json
from PIL import Image
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));import ai_helper as h
src=O/'r11_c14-internal-candidate-v1.png'
spec=[
('yard-upper',[1421,0],'Across local x627, the two diagonal golden sail spars have tiny stepped dark outlines and white bevel highlights. Reconnect each existing straight contour, preserving the real rope knots and the creamy triangular fabric folds. Also correct any artificial y1024 palette cut. Do not change the crop top115px.'),
('mast-upper',[1900,397],'At local y627 the upright mast and its adjacent soft shadow have abrupt paint jumps and small edge offsets. Connect both straight mast contours and their existing highlights through that cut. Continue existing fabric diagonal spar and bands through local x148 and x1172. Keep the real rope collar and exact spar intersections.'),
('dock-upper',[2842,397],'Across local y627 the wooden pier pile and adjacent diagonal pier beam have artificial tiny edge steps and palette changes. Continue the existing pile, its cool submerged shading and the beam contour. The ivory sail left edge at local x~280 also needs a continuous same outline, with unchanged existing fabric bands crossing local x230. Preserve rope windings and every real wooden joint.'),
('sail-middle-left',[1200,1421],'The ivory sail left edge and existing horizontal tan battens are interrupted by tiny artificial pixel steps across local y627 and x848. Continue the same batten edges, ivory folds and left sail outline. Preserve all real batten-end caps and left rope, do not add any batten, fold or line.'),
('mast-middle',[1900,1421],'The vertical mast near local x520 has a paint/outline split across local y627. Continue its existing straight outline and warm painted highlight through the split. Keep horizontal tan sail battens, fabric folds and the mast soft shadow continuous across the cut. No added joints or folds.'),
('sail-middle-right',[2445,1421],'Across local x627 the tan horizontal sail battens have small angular steps and discontinuous edges. Continue those same existing slightly diagonal batten outlines and fabric fold shading without extra divisions. At local y627 also join the curved right sail edge and the existing rope smoothly, keeping real end caps.'),
('sail-lower-left',[1200,2445],'Across local x848 and y627 the existing tan sail battens and cream folds have angular artificial little cuts. Continue existing contours and painted tones. Keep the sail left edge, every real batten end cap and boat rail behind it, without adding or erasing any true joint.'),
('mast-lower',[1900,2445],'Across local y627 the mast and its adjacent painted shadow show abrupt palette divisions. Join those existing straight contours and highlight. Keep every existing tan batten, fold and mast width unchanged; remove artificial tiny batten edge steps near x148 and x1172.'),
('sail-lower-right',[2445,2842],'Continue the existing horizontal tan sail batten outlines and bottom dark wooden boom through tiny artificial steps across local x627. Also remove local y230 fabric palette split. Preserve the right rope and real batten/boom end caps. Keep outer right115 and bottom115 pixels unchanged.'),
('boom-lower',[1421,2842],'Across local x627, the dark bottom sail boom and tan battens show tiny artificial angular interruptions. Reconnect their existing edges and highlights without changing line thickness. Preserve underlying boat rail, water, genuine boat joints and cloth fold count. Keep the bottom115 pixels unchanged.')
]
for n,xy,scene in spec:
 x,y=xy;p=O/(n+'-source.png');Image.open(src).crop((x,y,x+1254,y+1254)).save(p);h.derived(p,[src],{'method':'exact1254 native crop','crop':[x,y,x+1254,y+1254],'noResampling':True})
 prompt='Use case: precise-object-edit. Reference1 is the exact native1254x1254 repair target. '+scene+' Repair only the stated micro assembly cuts, smoothly connecting to the ORIGINAL contour positions outside the affected seam band. Preserve composition, camera, scale, geometry, all real construction joints, woodgrain and rope twist count. Reference2 is the actual approved style only: bright clean rounded Taoist Q-game handpainted finish. No UI, text, extra folds, extra objects, global recoloring, blur, warp or rescale. Output exactly1254x1254.'
 h.savecall(n,prompt,[p,h.STYLE],['exact native edit target','actual approved style04guild'])
(O/'ai-specs.json').write_text(json.dumps([{'name':n,'origin':xy,'task':s} for n,xy,s in spec],indent=2),encoding='utf8')
