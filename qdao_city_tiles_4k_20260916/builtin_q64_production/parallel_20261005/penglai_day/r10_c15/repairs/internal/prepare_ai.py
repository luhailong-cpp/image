from pathlib import Path
import json
from PIL import Image
import ai_helper as h
O=Path(__file__).resolve().parent
src=O/'r10_c15-internal-candidate-v1.png'
im=Image.open(src).convert('RGB')
jobs={'deck-rail':([397,0,1651,1254],'Repair artificial native-patch seam around x627: the deck plank groove at upper portion and the two diagonal front rails plus broad edge beam have tiny steps and split bevels. Make each existing groove and rail silhouette a single clean uninterrupted stroke across this narrow vertical seam; keep exact endpoints, perspective, object count, highlights and width. Harmonize split wood paint locally without adding joints.'),
'left-pile':([0,397,1254,1651],'Repair artificial horizontal seam around y627: the large front wooden post has an obvious angular paint-color divide and slight contour step; the thin rear diagonal brace left of it also has a tone split. Make both wood materials continuous and preserve every silhouette and exact beam count. No new join lines or hardware.'),
'right-pile':([2842,2445,4096,3699],'Repair artificial horizontal seam near y627 across central wooden pile and diagonal brace: remove angular wood-paint color boundary and reconnect the tiny outline/bevel stair steps. Keep exact pile width, round foot geometry, waterline ring and all other support structure.'),
'sail-spar':([1421,2842,2675,4096],'Repair artificial vertical seam near x627: golden sail spar diagonal at lower half has a tiny break in outline/highlight; water reflection above has artificial zigzag patch tone. Reconnect the spar with the same continuous straight contour and highlight, unify only the local water seam. Keep exact sail folds, spar width and existing objects.')}
for name,(box,desc) in jobs.items():
 crop=O/(name+'-source.png');im.crop(box).save(crop);h.derived(crop,[src],{'method':'exact1254native crop','boxLTRB':box,'resampling':False})
 prompt='Use case: inpainting seam repair. Image1 exact native1254 square source of continuous Taoist Q map. Image2 actually attached approved PRIMARY painting style, only style never UI. '+desc+' This is a localized repair, not redesign. Preserve all pixel-aligned geometry and composition outside the defective narrow seam, same scale/crop/camera. Bright clean rounded handpainted game art, no new objects, text, grain, blur or sharpening halos. Output exactly1254x1254.'
 h.savecall(name,prompt,[crop,h.STYLE],['native seam source','actual approved style 04-guild'])
jobs={k:{'cropLTRB':v[0],'finding':v[1]} for k,v in jobs.items()}
(O/'qa-findings-v1.json').write_text(json.dumps({'reviewed':['x1024','x2048','x3072','y1024','y2048','y3072','9junctions'],'repairs':jobs,'otherSeams':'remaining native-scale review acceptable with existing material variation; final review pending'},indent=2),encoding='utf8')
