from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day');OUT=ROOT/'qa/south-review'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((OUT/'crop-manifest.json').read_text())
diag=json.loads((OUT/'overlap-gradient-diagnostic.json').read_text())
dm={r['id']:r for r in diag['results']}
notes={
'v-r3-c1-2':('minor','Wood-grain brush shapes change across center seam. Pole silhouette and lower balustrade line have no gross discontinuity.',['paint_texture'],[176,0,208,1024]),
'v-r3-c2-3':('minor','Large paving joints and stone post contour continue; tiny native edge/paint differences remain around diagonal joins.',['minor_edge','paint_texture'],[176,0,208,1024]),
'v-r3-c3-4':('minor','Paving/curb diagonal lines continue. Foliage-shadow surface changes paint tone near seam; gradient best shift(-3,+2) is within4px Euclidean.',['shadow_tone','minor_edge'],[176,0,208,1024]),
'v-r4-c1-2':('moderate','Visible seam crosses leaf groups: left leaves have simpler broad shading, right leaves brighter outlined veins. Native outlines broadly correspond; require targeted local material/color transition and full-scale recheck. No new missing structural object identified.',['leaf_shading','vein_texture'],[176,260,208,990]),
'v-r4-c2-3':('minor','Stone stair wall and warm wooden edge remain continuous. Leaf and wall paint finish changes slightly at seam.',['paint_texture'],[176,0,208,1024]),
'v-r4-c3-4':('minor','Stair edges are continuous with no count change. Riser/tread brush tones change across seam. Parallel edges make translation along them weakly constrained: best(-6,+3) versus constrained(-2,+1) scores8.178/8.186; this is not evidence for >4px geometric correction.',['stair_texture','parallel_edge_alignment_ambiguity'],[176,0,208,1024]),
'h-r3-4-c1':('minor','Balustrade/post/wood pillar contours correspond. Stone face and wood brush patterns change along horizontal seam.',['paint_texture'],[0,176,1024,208]),
'h-r3-4-c2':('minor','Pole, rail opening and post align; horizontal shading change visible on rail and post.',['paint_tone'],[0,176,1024,208]),
'h-r3-4-c3':('minor','Paving joint and stair top contour remain continuous; broad pavement tone and native brush edge change at seam.',['paint_texture','minor_edge'],[0,176,1024,208]),
'h-r3-4-c4':('minor','All diagonal stair edges and right-side stone corner persist; subtle horizontal tone change across stair faces.',['paint_tone'],[0,176,1024,208]),
'cross-c1-2':('minor','Four-way meeting lies on wood pole; outer silhouette continuous. Internal wood paint/streak continuity needs final correction review.',['paint_texture'],[160,160,224,224]),
'cross-c2-3':('minor','Four-way meeting in paving between post and stair rail; no missing edge or inserted geometry seen. Small paint tone change persists.',['paint_tone'],[160,160,224,224]),
'cross-c3-4':('minor','Four-way stair meeting retains complete parallel contours; tread/riser texture changes need final assembly review.',['paint_texture'],[160,160,224,224]),
'corner-bottom-left':('none_in_available_pixels','Crisp rounded roof tile corner with continuous internal structure. Neighboring bottom tile pixels unavailable; this does not accept exterior seam.',['exterior_neighbor_unavailable'],[0,0,384,384]),
'corner-bottom-right':('none_in_available_pixels','Crisp ivory stair/landing corner, no missing pixels or blurred enlargement seen. Neighboring bottom/east tile pixels unavailable; exterior seams unverified.',['exterior_neighbor_unavailable'],[0,0,384,384])
}
items=[]
for item in manifest['items']:
 severity,note,tags,roi=notes[item['id']]
 item.update({'visuallyInspected':True,'inspectionScale':'1imagepixel=1sourcepixel; viewed full saved crop','severity':severity,'findings':note,'defectTypes':tags,'defectReviewRoiLTRB':roi,'diagnostic':dm.get(item['id']),'rawSeamAccepted':False,'aiStructuralRedrawRequiredNow':False,'next':'Root performs bounded registration/local color treatment if needed, then reviews actual final composite at native scale' if item['id'] in dm or item['id'].startswith('cross') else 'Retain as available corner evidence; exterior seams remain unverified'})
 items.append(item)
audit=[]
for n,info in manifest['nativeInputs'].items():
 p=Path(info['file']);rp=Path(str(p)+'.generation.json');rec=json.loads(rp.read_text(encoding='utf-8-sig'))
 pp=Path(rec['prompt']);im=Image.open(p)
 checks={'decode':True,'pixels1254':im.size==(1254,1254),'nativeShaMatchesRecord':sha(p)==rec['sha256'],'promptExists':pp.exists(),'toolResultPathPresent':bool(rec.get('toolResultPath')),'hintPresent':bool(rec.get('evidence',{}).get('toolOutputHint')),'submittedModelNull':rec['submittedParameters']['model'] is None,'submittedQualityNull':rec['submittedParameters']['quality'] is None,'actualModelNull':rec['actualModel'] is None,'actualQualityNull':rec['actualQuality'] is None,'allReferenceHashesMatch':all(Path(x['file']).exists() and sha(x['file'])==x['sha256'] for x in rec['references'])}
 audit.append({'id':n,'source':info,'record':str(rp),'recordSha256':sha(rp),'prompt':str(pp),'promptSha256':sha(pp),'checks':checks,'configTarget':rec['configSnapshot'],'allChecksPass':all(checks.values())})
report={'inspectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'native_south','tile':'r09_c13','scope':manifest['reviewScope'],'sourceCoreBoxLTRB':manifest['sourceCoreBoxLTRB'],'all15CropsViewed':True,'cropManifest':str(OUT/'crop-manifest.json'),'cropManifestSha256':sha(OUT/'crop-manifest.json'),'gradientDiagnostic':str(OUT/'overlap-gradient-diagnostic.json'),'gradientDiagnosticSha256':sha(OUT/'overlap-gradient-diagnostic.json'),'summary':'10raw1024pxseams+3crossings+2outerbottomcorners inspected. No missing geometry seen; visible leaf/paint/shadow tone transitions remain. No compulsory AI structural redraw identified in this subset. Do not accept raw composite. Apply only justified bounded geometry and local color corrections, preserve fields/masks and review root final16patch composite.','permittedDisplacementPixels':4,'displacementMetric':'Euclidean diagnostic constraint; no shifts applied','aiCalls':0,'nativeFilesModified':False,'wholeTileAccepted':False,'clientAccepted':False,'items':items,'metadataAudit':audit,'allMetadataChecksPass':all(x['allChecksPass'] for x in audit)}
(OUT/'south-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'report':str(OUT/'south-review.json'),'sha256':sha(OUT/'south-review.json'),'allMetadataChecksPass':report['allMetadataChecksPass'],'viewed':len(items)},indent=2))


