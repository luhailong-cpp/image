from pathlib import Path
import sys, json, hashlib, datetime
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent
JOINT = ROOT / 'repairs/left-edge/both-side'
OUT = ROOT / 'tiles/current'
QA = ROOT / 'qa/integrated-r09'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def source(path):
    return {'file': str(path), 'sha256': sha(path)}

def main(internal_path):
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    internal_path = Path(internal_path)
    proposal = json.loads((JOINT/'proposal-v3.json').read_text(encoding='utf-8-sig'))
    quilt_path, mask_path = Path(proposal['jointStrip']), Path(proposal['mask'])
    assert sha(quilt_path) == proposal['jointStripSha256']
    c12_source = Path(proposal['newC12'])
    assert sha(c12_source) == proposal['newC12Sha256']
    internal = Image.open(internal_path).convert('RGB')
    quilt = Image.open(quilt_path).convert('RGB')
    mask = Image.open(mask_path).convert('L')
    assert internal.size == (4096, 4096)
    assert quilt.size == mask.size == (1254, 4096)
    assert set(np.unique(np.asarray(mask))).issubset({0, 255})
    c13 = internal.copy()
    c13.paste(quilt.crop((627, 0, 1254, 4096)), (0, 0), mask.crop((627, 0, 1254, 4096)))
    revision = internal_path.stem.rsplit('-', 1)[-1]
    p13 = OUT/f'r09_c13-candidate-{revision}.png'
    c13.save(p13)
    c12 = Image.open(c12_source).convert('RGB')
    p12 = OUT/'r09_c12-candidate.png'
    c12.save(p12)
    mask13 = np.zeros((4096, 4096), dtype=bool)
    mask13[:, :627] = np.asarray(mask)[:, 627:] > 0
    unchanged = bool(np.array_equal(np.asarray(c13)[~mask13], np.asarray(internal)[~mask13]))
    assert unchanged
    handoff = json.loads((ROOT/'handoff.json').read_text(encoding='utf-8-sig'))
    old12_path = Path(handoff['baselineCandidates'][-1]['file'])
    assert sha(old12_path) == handoff['baselineCandidates'][-1]['sha256']
    old12 = Image.open(old12_path).convert('RGB')
    c12_left_unchanged = bool(np.array_equal(np.asarray(c12)[:, :3509], np.asarray(old12)[:, :3509]))
    assert c12_left_unchanged
    for n in range(4):
        box = (300, n*1024, 950, (n+1)*1024)
        c13.crop(box).save(QA/f'c13-repair-return-s{n+1}-native.png')
    board = Image.new('RGB', (950, 960))
    for n, y in enumerate((1024, 2048, 3072)):
        board.paste(c13.crop((0, y-160, 950, y+160)), (0, n*320))
    board.save(QA/'c13-return-intersections-native.png')
    overview = Image.new('RGB', (2048, 1024))
    overview.paste(c12.resize((1024, 1024), Image.Resampling.LANCZOS), (0,0))
    overview.paste(c13.resize((1024, 1024), Image.Resampling.LANCZOS), (1024,0))
    overview.save(ROOT/'current-pair-preview.png')
    c13.resize((1254,1254), Image.Resampling.LANCZOS).save(ROOT/'current-preview.png')
    record = {
        'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'integrated_candidate_pending_visual_review',
        'tilePixels': [4096,4096], 'formalAccepted': False,
        'wholeCityComplete': False, 'clientAccepted': False,
        'c12': source(p12), 'c13': source(p13),
        'derivedFrom': [source(internal_path), source(quilt_path), source(mask_path), source(c12_source)],
        'operation': 'Copy c12 revised candidate; replace only binary-mask-positive pixels from right half of native quilt into internally corrected c13. No scaling, displacement, blur or feather in this integration.',
        'internalPixelsOutsideMaskIdentical': unchanged,
        'c12Left3509ColumnsUnchanged': c12_left_unchanged,
        'oldC12SourceFileUnchanged': True,
        'priorCorrections': 'See source records for earlier bounded subpixel registration, color fields, native overlap cuts and AI edits. This integration does not erase those processing histories.',
        'qaDirectory': str(QA),
    }
    write(OUT/f'integration-{revision}.json', record)
    write(OUT/'integration.json', record)
    write(str(p12)+'.generation.json', {'file':str(p12),'sha256':sha(p12),'derivedFrom':[source(c12_source)],'operation':'lossless RGB PNG export, unchanged pixels','productionArt':False,'formalAccepted':False})
    write(str(p13)+'.generation.json', {'file':str(p13),'sha256':sha(p13),'derivedFrom':record['derivedFrom'][:3],'operation':record['operation'],'productionArt':False,'formalAccepted':False})
    print(json.dumps(record, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1])
