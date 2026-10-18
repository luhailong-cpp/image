"""Independent byte replay of recovered native candidate and hash-bound review.
Does not alter artwork, source selection, global progress, or old QA files.
"""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib
import numpy as np

T = Path(__file__).resolve().parent
Q = T / 'qa/full-native-20261016-v1'
E = T.parent / 'seam-qa/r08_c10-full-native-20261016-v1'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, d):
    assert not p.exists(), p
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
selection = T / 'selected-patches.json'
sel = read(selection)
m = read(Q / 'manifest.json')
assert sha(selection) == m['selectionSha256']
assert len(sel['patches']) == 16 and len(m['evidence']) == 33
rows, sources = [], []
for r in range(1, 5):
    row = []
    for c in range(1, 5):
        pid = f'p{r}{c}'
        p = T / sel['patches'][pid]
        meta = next(s for s in m['sources'] if s['patch'] == pid)
        assert sha(p) == meta['sha256']
        a = np.asarray(Image.open(p).convert('RGB'))
        assert a.shape == (1254, 1254, 3)
        row.append(a[115:1139, 115:1139].copy())
        sources.append({'patch': pid, 'file': str(p), 'sha256': sha(p), 'size': [1254,1254], 'crop': [115,115,1139,1139]})
    rows.append(np.concatenate(row, axis=1))
replay = np.concatenate(rows, axis=0)
candidate = Q / 'candidate-4096.png'
actual = np.asarray(Image.open(candidate).convert('RGB'))
assert actual.shape == (4096,4096,3)
assert np.array_equal(actual, replay)
assert sha(candidate) == read(candidate.with_suffix('.png.derivation.json'))['sha256']
ox, oy = 36864, 28672
evidence = []
for item in m['evidence']:
    p = Path(item['file'])
    assert sha(p) == item['sha256']
    x0,y0,x1,y1 = item['globalBox']
    a = np.asarray(Image.open(p).convert('RGB'))
    assert np.array_equal(a, replay[y0-oy:y1-oy,x0-ox:x1-ox])
    evidence.append({'file':str(p),'sha256':sha(p),'pixelReplayIdentical':True})
stamp = datetime.now(timezone.utc).isoformat()
audit = {'tile':'r08_c10','createdAt':stamp,'selection':{'file':str(selection),'sha256':sha(selection)},
 'candidate':{'file':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096]},
 'sources':sources,'nativeCoreCount':16,'coreSize':[1024,1024], 'pixelCoverage':4096*4096,
 'assemblyMethod':'Independent NumPy row/column concatenation of original [115:1139,115:1139] source samples',
 'candidatePixelReplayIdentical':True,'maxChannelDifference':0,'differentChannels':0,
 'QAReplayCount':len(evidence),'evidence':evidence,'resamplingApplied':False,'layoutPixelsUsed':False,
 'singleGeneration4K':False,'internalReady':False,'formalAccepted':False,'actualModel':None}
save(T/'independent-replay-20261017-v1.json',audit)

notes = {
 'p11--p12': 'Visible vertical material cut and rectangular lower-right texture line; stone pattern phase changes.',
 'p11--p21': 'Small stone edge and texture transition; retain pending with top-row correction.',
 'p12--p13': 'Stone joint phase and material scale differ; lower horizontal rectangular line visible.',
 'p12--p22': 'Strong horizontal rectangular texture line ~34 px above nominal seam; stone joints discontinuous.',
 'p13--p14': 'Stone diagonals kink near center boundary; horizontal line near lower edge.',
 'p13--p23': 'Horizontal line ~34 px above nominal seam, stone mottling switches at line.',
 'p14--p24': 'Horizontal texture line ~34 px above seam and mismatched paving behind dock.',
 'p21--p22': 'Stone joint width/phase discontinuity and material contrast at vertical cut.',
 'p23--p24': 'Wood overall geometry connects; background paving has jog, local grain transition pending.',
 'p23--p33': 'Pier remains broadly continuous; right silhouette width/grain transition requires coordinated review.',
 'p24--p34': 'Horizontal wood-grain/lighting step in dock face and minor water transition.',
 'p31--p32': 'Dock connects; paving joint corner and wood-grain transition remain visible.',
 'p32--p33': 'Clear vertical shift in plank edges, dock lower contour and water texture.',
 'p33--p34': 'Boat inner rim/bottom geometry kinks at central vertical join; preserve pending.',
 'p33--p43': 'Pier right contour/grain transition and water caustics need reconciliation.',
 'p34--p44': 'Boat outline connects; floor-board grain transition near horizontal seam.',
 'p41--p42': 'Water caustic pattern changes at vertical join; post/dock broadly continuous.',
 'p42--p43': 'Water brightness and caustic scale change across vertical boundary.',
 'p43--p44': 'Boat silhouette broadly continuous; caustic continuity remains pending.',
 'cross-r1-c1':'Top-right rectangular texture boundary and shifted paving joints.',
 'cross-r1-c2':'Horizontal rectangular texture line and stone phase switch.',
 'cross-r1-c3':'Horizontal line, diagonal stone joint kink and lower paving jog.',
 'cross-r2-c1':'Stone joint/corner phase and mottling change at cross.',
 'cross-r2-c3':'Horizontal dock-face texture step on right half.',
 'cross-r3-c2':'Vertical dock contour/water transition at top center.',
 'cross-r3-c3':'Boat floor/rim grain transition; geometry review remains pending with p33/p34.'}
reviews=[]
for item in evidence:
    key=Path(item['file']).stem
    reviews.append(dict(item,viewedAtNativeResolution=True,reviewMethod='view_image original resolution',
       status='pending_repair' if key in notes else 'visually_usable_local_crop',
       note=notes.get(key,'No obvious structural break in this viewed crop; tile-level pending issues and external acceptance still apply.'), formalAccepted=False))
external=[]
for p in sorted(E.glob('*-100pct.png')):
    meta=read(p.with_name(p.name.replace('-100pct.png','.qa.json')))
    image_meta=meta.get('image',{})
    if image_meta and image_meta.get('sha256'): assert sha(p)==image_meta['sha256']
    name=p.stem
    if name.startswith('west') or 'x36864' in name:
        note='Paving joint phase, stone material/density or corner mismatch visible; west segment 4 and southwest corner include stronger discontinuity.'
    elif 'segment-1' in name or 'x37888' in name:
        note='South stone/rail material and local alignment transition remains pending; main rail/post shape broadly connects.'
    else:
        note='Water caustic/detail transition remains pending; boat/post silhouettes broadly connected where present.'
    external.append({'file':str(p),'sha256':sha(p),'viewedAtNativeResolution':True,'status':'pending_repair','note':note,'formalAccepted':False})
review={'tile':'r08_c10','createdAt':stamp,'selectedNativeCount':16,'candidate':audit['candidate'],
 'independentReplay':{'file':str(T/'independent-replay-20261017-v1.json'),'sha256':sha(T/'independent-replay-20261017-v1.json')},
 'nativeReviews':reviews,'nativeReviewCount':33,'externalReviews':external,'externalViewedCount':len(external),
 'pending':[{'location':k,'issue':v} for k,v in notes.items()]+[
 {'location':'west p41 and southwest corner','issue':'Stone joint displacement and texture phase; earlier two repairs did not resolve fully. Keep p41-v3 provisional, no third immediate same-point loop.'},
 {'location':'north/east external','issue':'Unavailable selected neighbor sources in existing zone-reader evidence; not reviewed, not claimed globally absent.'}],
 'status':'native_4k_saved_internal_and_external_repairs_pending','internalReady':False,'formalAccepted':False,
 'actualModel':None,'route':'builtin','sourceSelectionUnchanged':True,
 'next':'Continue independently audited r08_c11 along existing selected west cores. Avoid copying unselected halos or propagating pending internal stone/grid defects.'}
save(T/'review-recovery-20261017-v1.json',review)
print(json.dumps({'candidate':audit['candidate'],'replay':True,'internalQA':33,'externalViewed':len(external),'internalReady':False,'formalAccepted':False}))
