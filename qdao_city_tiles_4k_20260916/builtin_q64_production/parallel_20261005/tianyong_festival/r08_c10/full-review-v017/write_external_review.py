from pathlib import Path
import json,hashlib

out=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
index_path=out/'external-crop-index.json'
index=json.loads(index_path.read_text(encoding='utf-8'))
record={
 'reviewedAtUtc':'2026-10-08 11:08:50 UTC',
 'reviewer':'external_review',
 'scope':'r08_c09/r08_c10 entire 4096-pixel shared vertical boundary, native 384-pixel context on each side, existing corner source portions, and verification of unchanged south band against earlier root review',
 'sourceCheckpoint':index['checkpoint'],
 'sources':index['sources'],
 'cropIndex':{'file':str(index_path),'sha256':sha(index_path)},
 'reviewedImages':index['crops'],
 'nativePixelInspection':True,'nativeScale':1,'newModelCalls':0,'sourceImagesModified':False,
 'localVisualAccepted':True,'leftSharedBoundaryAccepted':True,'wholeTileAccepted':False,'formalAccepted':False,
 'findings':[
   {'id':'left-upper','tileLocalY':[0,1152],'finding':'Inspected native 768x1152 strip. Slate inset perimeter and diagonal ivory courses remain continuous through the x0 boundary. No new doubled edge, block-aligned line break or vertical colour return is visible.'},
   {'id':'left-middle-upper','tileLocalY':[1024,2176],'finding':'Inspected native 768x1152 strip. Broad curved ivory course, recessed beige panel and border highlights pass through the boundary naturally. Low-contrast veining continues without a conspicuous boundary-aligned step.'},
   {'id':'left-middle-lower','tileLocalY':[2048,3200],'finding':'Inspected native 768x1152 strip. Curved band and two transverse panel joints remain connected across x0; contour thickness and material shading do not show an unacceptable join.'},
   {'id':'left-lower','tileLocalY':[3072,4096],'finding':'Inspected native 768x1024 strip. Curving panel edge, lower transverse divider and outer channel remain visually continuous through the current tile boundary.'},
   {'id':'inherited-y2048-y3072','tileLocalY':[2048,3072],'finding':'Additionally inspected native 768x256 windows centred on each inherited horizontal source transition. The pre-existing wider c09 defects are not accepted or dismissed globally by this review. At the actual c09/c10 vertical join in these windows, no unacceptable discontinuity, doubled bevel or horizontal break is visible. Defects farther west are not attributed to the new c10 tile.'},
   {'id':'southwest-four-tile-junction','finding':'Inspected native 768x768 four-tile junction using the current c09/c10 row8 and row9 sources. Ivory course, narrow channel, bevel and slate inset are continuous across the cross. No visible rectangular return or four-way colour split.'},
   {'id':'partial-corners','finding':'Northwest known southern half, northeast known southwest quarter, and southeast known western half were inspected at native scale. Known source portions are intact. Transparent space in QA canvases denotes missing/unaccepted neighbours and is excluded from acceptance.'}
 ],
 'southReference':dict(index['southReference'],status='Earlier root full-width south-boundary visual acceptance remains applicable: current active south256 rows exactly equal v014; bottom source is unchanged current v009. This audit does not claim to have repeated the entire south review.'),
 'supplementalMetricsNotAcceptance':index['supplementalMetricsNotAcceptance'],
 'pending':[
  {'edge':'north','reason':'r07 neighbours are not part of the root-accepted current candidate set. Complete north seam and north corner acceptance require accepted actual neighbour files.'},
  {'edge':'east','reason':'r08_c11 and eastern corner neighbours are not available in the current candidate set. No complete east seam acceptance is claimed.'},
  {'scope':'formal map acceptance','reason':'This record does not cover internal seams, geometry/navigation, whole-city completion or nearest-camera runtime validation.'}
 ]
}
p=out/'external-left-review.json'
p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':sha(p),'leftSharedBoundaryAccepted':True,'formalAccepted':False},ensure_ascii=False))
