from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
import hashlib
import json
from PIL import Image

BASE = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
B = BASE / 'parallel-production-20261013/village-west-courtyard'
OUT = Path(__file__).resolve().parent
WEST = BASE / 'fishing-village-game-20261009/southwest/qa'
EAST = B / 'repairs/r13c06-north-external-oct16-v1/final-candidate-v2'
expected = {
    'west_assembly': 'e691874f7e44b2466f0455b40719ea7c598e2fee6552286ace23fa3e05b6e73f',
    'west_candidate': '2afcd0758dee49ae02041523b624b73d94f5c17d0450ebada0ebff3ca72853cb',
    'east_context': '7ba8f8f494a8243dc5b1bdffaadf806cb714be67ca688b052703756a72627283',
}
paths = {
    'west_assembly': WEST / 'full-tile-r13_c05-assembly.json',
    'west_candidate': WEST / 'full-tile-r13_c05-candidate-4096.png',
    'west_context': WEST / 'full-tile-r13_c05-context-native.png',
    'east_assembly': EAST / 'assembly.json',
    'east_candidate': EAST / 'r13_c06.candidate-native-4096.png',
    'east_context': EAST / 'context-native.png',
}
def sha(data):
    return hashlib.sha256(data).hexdigest()

started = datetime.now(timezone.utc).isoformat()
inputs = {}
data = {}
images = {}
assemblies = {}
for key, path in paths.items():
    blob = path.read_bytes()
    data[key] = blob
    record = {'path': path.as_posix(), 'sha256': sha(blob), 'bytes': len(blob),
              'readAtUtc': datetime.now(timezone.utc).isoformat(),
              'mtimeUtc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
    if key in expected:
        record['expectedSha256'] = expected[key]
        record['expectedHashMatches'] = record['sha256'] == expected[key]
        assert record['expectedHashMatches'], key
    if path.suffix == '.png':
        images[key] = Image.open(BytesIO(blob)).convert('RGB')
        record['size'] = list(images[key].size)
    else:
        assemblies[key] = json.loads(blob.decode('utf-8-sig'))
    inputs[key] = record

assert images['west_candidate'].size == images['east_candidate'].size == (4096, 4096)
assert images['west_context'].size == images['east_context'].size == (4326, 4326)
for side in ['west', 'east']:
    assert images[side+'_context'].crop((115,115,4211,4211)).tobytes() == images[side+'_candidate'].tobytes()

wa = assemblies['west_assembly']
ea = assemblies['east_assembly']
assert inputs['west_context']['sha256'] == wa['context']['sha256']
assert inputs['west_candidate']['sha256'] == wa['output']['sha256']
assert inputs['east_context']['sha256'] == ea['finalContext']['sha256']
assert inputs['east_candidate']['sha256'] == ea['final4096']['sha256']
source_checks = []
for s in wa['sources']:
    p = Path(s['path'])
    h = sha(p.read_bytes())
    source_checks.append({'patch': s['patch'], 'path': p.as_posix(), 'sha256': h,
                          'assemblySha256': s['sha256'], 'matches': h == s['sha256']})
assert len(source_checks) == 16 and all(s['matches'] for s in source_checks)

outputs = []
for i in range(4):
    y = i*1024
    contact = Image.new('RGB',(460,1024))
    west_box = (3866,y,4096,y+1024)
    east_context_box = (115,115+y,345,115+y+1024)
    west_crop = images['west_candidate'].crop(west_box)
    east_crop = images['east_context'].crop(east_context_box)
    contact.paste(west_crop,(0,0))
    contact.paste(east_crop,(230,0))
    assert contact.crop((0,0,230,1024)).tobytes() == west_crop.tobytes()
    assert contact.crop((230,0,460,1024)).tobytes() == east_crop.tobytes()
    name = f'contact-part{i+1:02d}-y{49152+y}-{50176+y}-100pct.png'
    p = OUT / name
    assert not p.exists(), str(p)
    contact.save(p)
    outputs.append({'path':p.as_posix(),'sha256':sha(p.read_bytes()),'size':[460,1024],
                    'westCandidateCropBox':list(west_box),'eastContextCropBox':list(east_context_box),
                    'globalBox':[20250,49152+y,20710,50176+y],
                    'seamLocalX':230,'globalSeamX':20480,
                    'westStripPixelsExactlyVerified':True,'eastStripPixelsExactlyVerified':True})

for key,path in paths.items():
    inputs[key]['unchangedAfterCrop'] = sha(path.read_bytes()) == inputs[key]['sha256']
assert all(r['unchangedAfterCrop'] for r in inputs.values())
manifest = {
    'schemaVersion':1, 'snapshotStartedAtUtc':started,
    'snapshotFinishedAtUtc':datetime.now(timezone.utc).isoformat(),
    'task':'r13_c05 east core / r13_c06 west core actual external join diagnostic',
    'status':'pending-visual-inspection',
    'formalAccepted':False, 'stableGenerationAnchor':False,
    'westStatusAtSnapshot':wa['status'],'eastStatusAtSnapshot':ea['status'],
    'globalSeam':{'x':20480,'yHalfOpen':[49152,53248]},
    'globalContactBox':[20250,49152,20710,53248],
    'method':'Integer 230-pixel core crops each side, directly juxtaposed to 460x1024, four segments. No scaling, blending, drawing, colour or geometry change.',
    'boxConvention':'[left,top,right,bottom) half-open integer pixel bounds',
    'candidateContextCropEquality':{'west':True,'east':True,'crop':[115,115,4211,4211]},
    'inputs':inputs,'west16SourceHashChecks':source_checks,'outputs':outputs,
    'reuseRule':'Diagnostic snapshot only. Recheck any touched region after either candidate/context/assembly changes. Root is actively repairing southern r13_c06. No automatic reuse of changed southern segment or promotion of r13_c05 as stable anchor.',
    'verificationLimit':'Hash, source count and crop equality verify identity/provenance only; they do not establish visual seam acceptance.',
}
p = OUT/'snapshot-manifest.json'
assert not p.exists(),str(p)
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'snapshotStartedAtUtc':started,'snapshotFinishedAtUtc':manifest['snapshotFinishedAtUtc'],
                  'west16SourcesVerified':len(source_checks),'outputs':outputs},ensure_ascii=False,indent=2))
