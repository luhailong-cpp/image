from pathlib import Path
import sys,json
from PIL import Image
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));import ai_helper as h
src=O/'r11_c15-internal-candidate-v4.png'
spec=[('boom-return',[1870,1480], 'The long nearly horizontal golden boom has a tiny angular jump through its upper edge, highlight and lower edge around x600,y610. Repaint only a short stretch around this unwanted cut to connect the existing straight contours. KEEP the exact original position of each contour at x400 and x850; smoothly join between these fixed endpoints. Preserve the mast collar and all true joints.'),('post-return',[950,413], 'A small wooden upright beside the left edge of the cream sail has an artificial tiny angular step on its dark lower diagonal outline near x605,y620. Repair that tiny contour while keeping the exact existing endpoints on either side. Preserve the real diagonal deck plank grooves, sail edge, and every object.'),('hull-return',[1421,2445], 'Several diagonal wood plank grooves and long golden rail highlights have tiny artificial angular cuts around x~400..820, y~540..900. Remove only those tiny steps, joining the EXISTING endpoints smoothly. Keep the genuine dark vertical plank joint and all cross-board joints. Preserve the boat geometry, planks, post and shadows.')]
for name,xy,scene in spec:
 p=O/(name+'-source.png');x,y=xy;Image.open(src).crop((x,y,x+1254,y+1254)).save(p);h.derived(p,[src],{'crop':[x,y,x+1254,y+1254],'nativeNoRescale':True})
 prompt='Edit reference1 at its exact1254x1254 native size. Micro seam inpainting, preserve the composition and all geometry. '+scene+' Keep the outer250px frame unchanged and match its colors. The tiny repair must flow into the original contours without shifting whole lines. Reference2 is actual approved style only: bright clean rounded polished Taoist Q-game handpainting. No UI, text, additions, blurring, resizing, sharpening halos, or global recoloring.'
 h.savecall(name,prompt,[p,h.STYLE],['native exact crop of current composite requiring micro seam repair','approved actual style04guild'])
(O/'finish-spec.json').write_text(json.dumps(spec),encoding='utf8')
