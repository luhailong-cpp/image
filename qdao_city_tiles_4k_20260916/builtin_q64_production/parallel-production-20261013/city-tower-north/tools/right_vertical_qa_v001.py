import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
ASSEMBLY = BASE / 'versions/root-r03c14-full-assembly-v002/r03_c14/assembly/assembly.json'
M = json.loads(ASSEMBLY.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_group(number, observations):
    candidate = M['artifacts'][0]
    assert sha(candidate['file']) == candidate['sha256']
    seams = [s for s in M['internalSeamSegments'] if Path(s['file']).name.startswith('vertical-')][4*(number-1):4*number]
    assert len(seams) == len(observations) == 4
    results = []
    for seam, observation in zip(seams, observations):
        assert sha(seam['file']) == seam['sha256']
        assert list(Image.open(seam['file']).size) == [384, 1024]
        source_ids = seam['sourceIds']
        sources = [s for s in M['selectedNative'] if s['patch'] in source_ids]
        for source in sources:
            assert sha(source['file']) == source['sha256']
        defects = observation.get('defects', [])
        for defect in defects:
            x0,y0,x1,y1 = defect['bboxSeamPixels']
            cx,cy = seam['crop'][:2]
            defect['bboxTilePixels'] = [x0+cx,y0+cy,x1+cx,y1+cy]
        results.append({'seam': Path(seam['file']).stem, 'evidence': seam, 'selectedNative': sources,
                        'reviewedAtOriginalPixels': True, 'seamLocalX':192, **observation})
    report = {'schemaVersion':1, 'createdAtUtc':datetime.now(timezone.utc).isoformat(),
              'reviewer':'tower_right', 'tile':'r03_c14', 'candidate':candidate,
              'assemblyManifest':{'file':str(ASSEMBLY),'sha256':sha(ASSEMBLY)},
              'selection': M['selection'], 'scope':'Four vertical internal seam crops only; no horizontal or external seam acceptance.',
              'group':number, 'grouping':'Assembly manifest order: four rows per vertical boundary.',
              'bboxConvention':'Half-open [x0,y0,x1,y1], native integer pixels.',
              'mechanicalEvidence':'Candidate, seam crops and selected native source hashes verified against assembly manifest.',
              'formalAcceptedCount':0, 'newImagesGenerated':0, 'results':results,
              'localPassCount':sum(r['status']=='local-pass' for r in results),
              'needsRepairCount':sum(r['status']=='needs-repair' for r in results)}
    out = BASE / f'qa/right-r03c14-vertical-group{number}-v001.json'
    with out.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'file':str(out),'sha256':sha(out),'localPassCount':report['localPassCount'],'needsRepairCount':report['needsRepairCount']},ensure_ascii=False))

if __name__ == '__main__':
    save_group(1, [
        {'status':'local-pass','observation':'红梁金饰、金脊分节边和蓝瓦筒跨 x=192 连续，未见结构跳变。','defects':[]},
        {'status':'local-pass','observation':'红柱及上方金色卷饰、底端金脊首节跨缝连续；未见柱宽或构件相位变化。','defects':[]},
        {'status':'local-pass','observation':'上段金脊和蓝瓦、下段檐梁及红柱金饰跨缝连续。','defects':[]},
        {'status':'local-pass','observation':'红柱、金脊各节以及两侧蓝瓦跨缝连续；未见新增断边或错层。','defects':[]},
    ])
    image = Image.open(M['artifacts'][0]['file'])
    out = BASE / 'qa/right-r03c14-p32-p33-top-context-100pct-v001.png'
    assert not out.exists()
    image.crop((1664,1792,2432,2304)).save(out)
    print(json.dumps({'file':str(out),'sha256':sha(out),'crop':[1664,1792,2432,2304],'size':[768,512],'resized':False}))
