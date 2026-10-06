from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image

out=Path(__file__).resolve().parent/'early-vertical-qa';p=out/'manifest.json'
j=json.loads(p.read_text(encoding='utf-8'))
notes={
 'vertical_c1_r1':'Paving grooves and lantern cap are continuous at x1024; mild broad stone brush variation retained.',
 'vertical_c2_r1':'Diagonal slab groove crosses x2048 without an evident step; no straight tonal split.',
 'vertical_c3_r1':'Both grooves and original soft tree shadows continue at x3072; no added geometry or rectangular band.',
 'vertical_c1_r2':'Red shaft, gold rings and blank inset remain continuous at x1024. Highlight changes follow painted form, not a disconnected seam.',
 'vertical_c2_r2':'Paving groove, soft tree shadow and clipped bridge-pillar portions have no obvious artificial break at x2048.',
 'vertical_c3_r2':'Slab grooves, upper bridge rail and opening contours stay connected at x3072; gray material brush variation remains.',
 'vertical_c1_r3':'Blank gold inset and layered lantern base cross x1024 coherently; no cut-off decorative shape or vertical color stripe.',
 'vertical_c2_r3':'Bridge pillar, rail opening and arch left edge connected. Narrow vertical shade beside post is a natural depth/bevel transition, not an unsupported guide wall.',
 'vertical_c3_r3':'Large arch face, curved rim and original radial joint connected at x3072; masonry bevel highlight varies slightly but no clear displaced contour.',
 'guide_vertical_c2_r1':'Quiet paving and original groove continue through x1139; no reproduced guide-edge strip.',
 'guide_vertical_c3_r1':'Diagonal paving groove and broad low-contrast paint coherent at x2163.',
 'guide_vertical_c4_r1':'Existing soft shadow and bottom groove continuous at x3187; no sharp guide boundary.',
 'guide_vertical_c2_r2':'Lantern arm, post contour and inset border retain original shape through x1139. No extra objects from neighboring image.',
 'guide_vertical_c3_r2':'Stone post, diagonal groove and tree shadow remain coherent through x2163.',
 'guide_vertical_c4_r2':'Rail aperture interior has restrained bevel variation; its outlines and surrounding paving show no detached line at x3187.',
 'guide_vertical_c2_r3':'Red/gold post edge, base and pale curb coherent at x1139; no old artificial gold horizontal band visible in this scope.',
 'guide_vertical_c3_r3':'Rail aperture, broad arch face and foreground post continuous through x2163.',
 'guide_vertical_c4_r3':'Large arch and dark underside continuous at x3187, with restrained existing gray stone texture.',
 'intersection_r1_c1':'Four-cell meeting around red shaft: cap, shaft highlights and crossarm are continuous, no rectangular meeting mark.',
 'intersection_r1_c2':'Four-cell stone paving meeting coherent; two original diagonal grooves continuous. Small bridge side remains naturally clipped at crop edge.',
 'intersection_r1_c3':'Parallel diagonal paving grooves remain coherent; mild stone paint variation has no hard crossing-shaped seam.',
 'intersection_r2_c1':'Blank gold lantern panel spans the four-cell crossing with coherent framing and shading; no text or new line.',
 'intersection_r2_c2':'Bridge pillar, support bevel and rail opening meet coherently. Gray side shade at the junction follows existing volume.',
 'intersection_r2_c3':'Upper aperture, curved rail base and arch masonry joint retain connected contours at the four-cell meeting.'}
assert len(j['checks'])==len(notes)==24
for check in j['checks']:
    path=Path(check['file']);assert hashlib.sha256(path.read_bytes()).hexdigest()==check['sha256']
    check.update(actualViewed=True,viewMethod='tools.view_image(detail=original)',
        observation=notes[path.stem],requiresRepair=False,
        decodedRgbSha256=hashlib.sha256(Image.open(path).convert('RGB').tobytes()).hexdigest())
j.update(reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',qaStatus='all24_actually_viewed_no_required_repair_identified',
    coverage={'verticalSeamSegments':9,'verticalGuideBandSegments':9,'fourCellIntersections':6},
    remaining='Fourth-row scopes, lower intersections, outer edges and final candidate provenance remain pending.',
    formalAccepted=False,wholeCityComplete=False)
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'viewed':24,'reportSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
