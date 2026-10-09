from pathlib import Path
from PIL import Image
import ai_helper as a
import json
O=a.O
src=O/'r10_c14-internal-candidate-v2.png'
specs={
 'stonecap':dict(origin=[1500,397],scene='Two ivory stone parapet uprights and sloping rail. Remove the artificial small lateral steps or jagged notches in the dark outer contours and bright bevels at horizontal band y540..740 of this crop. Especially the left outer contour of each pale upright must be one smooth uninterrupted curve/vertical. Preserve all stone block divisions, camera and silhouettes away from those tiny erroneous steps. Unify their stone material.'),
 'wallmiddle':dict(origin=[1000,1421],scene='Broad pale stone retaining wall panels. Remove the artificial lateral step or short fork in the near vertical stone groove at x470 around y600 of this crop, joining upper and lower portions into one smoothly continuous narrow recessed dark groove with slim pale bevel. Preserve other panel joints and diagonal upper coping. Unify the stone paint across horizontal y627 band with no rectangular field seam.'),
 'wallright':dict(origin=[1940,1421],scene='Stone wall and large rounded pale pier at right, water at bottom, cropped rope jetty at lower left. Remove artificial small step or fork in near vertical wall groove at x315 around y650, and artificial short blocky lateral step in soft blue vertical shadow boundary around x900 y640; continue both naturally and smoothly. Eliminate any residual rectangular horizontal patch boundary at y627. Preserve true panel joints, pier silhouette, waterline, object geometry and camera.'),
 'tilebevel':dict(origin=[397,750],scene='Pale warm stone harbor paving with cropped bronze mooring fixture and stone parapet. Repair tiny white angular notch and microstep in long diagonal paving bevel near x625 y570. That tile bevel and its narrow dark groove should be smoothly continuous and uniform width. Preserve every true tile corner, bronze fixture, stone parapet shape and all positions. Do not add any extra grooves.')
}
for name,s in specs.items():
 x,y=s['origin'];p=O/(name+'-edit-input.png');Image.open(src).crop((x,y,x+1254,y+1254)).save(p);a.derived(p,[src],{'method':'native1254 crop, no resize','origin':s['origin']})
 prompt='Use case: inpainting/local structural cleanup. Image1 is the exact native1254 square artwork to repair at identical scale/camera/crop. Image2 is approved primary painting style, not content. '+s['scene']+' Keep the same clean bright rounded Taoist Q game painting and restrained handpainted materials. Repaint only to remove those continuity defects; never copy an artificial source seam. No new objects, no composition changes, no blur or enlargement, no text/UI. Return same square crop.'
 a.savecall(name+'-ai-v1',prompt,[p,a.STYLE],['exact native repair input','approved primary style only'])
(O/'ai-repair-specs.json').write_text(json.dumps({'base':str(src),'baseSha256':a.sha(src),'specs':specs},indent=2))
print(list(specs))
