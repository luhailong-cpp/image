from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
from PIL import Image
import ai_helper as h
O=Path(__file__).resolve().parent
src=O/'r09_c15-internal-candidate-v1.png'
im=Image.open(src).convert('RGB')
specs={'cliff':{'origin':[2445,0],'issue':'a false vertical tonal seam near x627 across rock faces. Repaint only the narrow vertical strip x450..790 over full height to make each rock face and foliage continuous. Preserve every existing long rock fissure and all plant silhouettes.'},'post':{'origin':[397,1421],'issue':'horizontal assembly at y627 makes tiny artificial stair steps in both edges of the central tall golden wood post around x555 and x655. Repair continuous straight post edges, continuous wood grain and adjacent ivory cloth across y440..790. Do not add any bevel or split in the post.'},'leaf':{'origin':[930,2445],'issue':'horizontal assembly around y627 clips the tips of lime-green leaves near x620..760 and interrupts wood grain at the left post. Reconstruct the same existing leaf tips, no new leaves, and make the existing post and background rail continuous across y440..790.'},'rightpost':{'origin':[2100,2445],'issue':'horizontal assembly around y627 creates a tiny step in the left edge of golden post near x520..650, and slight wood-grain split. Restore the same straight post edges and continuous nearby rail and ivory cloth in narrow y450..790. Keep all existing counts, boundaries and shadows.'}}
for n,s in specs.items():
 x,y=s['origin'];p=O/(n+'-edit-input.png');im.crop((x,y,x+1254,y+1254)).save(p);h.derived(p,[src],{'method':'exact native integer1254crop','boxLTRB':[x,y,x+1254,y+1254],'noScaling':True})
 prompt='Native image edit, seamless game-map repair. Image1 is the actual1254x1254 painted input. Image2 is the required approved style reference only; no UI. Keep Image1 exact camera, framing, object count, structure, scale and native pixel geometry. Repair this specific issue: '+s['issue']+' Retain clean rounded bright Taoist Q hand-painted art. Preserve all other pixels and especially outer context. No new objects, extra shadow, denser foliage, blur, rescaling or sharpening. Output exactly1254x1254 pixels.'
 h.savecall(n+'-ai-v1',prompt,[p,h.STYLE],['native edit crop1254, composition and pixel geometry','actual approved painting style04-guild'])
(O/'repair-specs.json').write_text(json.dumps(specs,indent=2),encoding='utf8')
