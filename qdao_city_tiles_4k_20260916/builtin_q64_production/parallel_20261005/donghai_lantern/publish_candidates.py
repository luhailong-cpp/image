"""Verified current pixel candidates and previews; no formal/client acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, sys, tempfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / 'current-candidates.json'

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, value):
    p = Path(p).resolve()
    assert p.is_relative_to(ROOT), p
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.publish-', dir=p.parent)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
    os.replace(tmp, p)

def initial():
    h = read(ROOT / 'handoff.json')
    return {'schemaVersion': 2, 'appearance': 'donghai_lantern',
            'activeTile': 'r08_c13', 'formalAccepted': False, 'clientAccepted': False,
            'wholeCityComplete': False, 'candidates': [
                {'tile': Path(e['file']).stem, 'file': e['file'], 'sha256': e['sha256'],
                 'baseline': True, 'qaStatus': 'historical_candidate_scoped_checks',
                 'qaRecords': [], 'completePixelCandidate': True}
                for e in h['baselineCandidates']]}

def verify(entry):
    p = Path(entry['file'])
    assert p.is_file() and sha(p) == entry['sha256'], p
    with Image.open(p) as im:
        im.load()
        assert im.format == 'PNG' and im.size == (4096, 4096), p
        if im.mode == 'RGBA': assert im.getchannel('A').getextrema() == (255, 255)
    for q in entry.get('qaRecords', []): assert Path(q).is_file(), q

def status():
    registry = read(REGISTRY) if REGISTRY.exists() else initial()
    entries = sorted(registry['candidates'], key=lambda e: e['tile'])
    assert len({e['tile'] for e in entries}) == len(entries)
    for entry in entries: verify(entry)
    complete = {e['tile']: e for e in entries}
    active = registry['activeTile']
    native_dir = ROOT / active / 'native'
    natives = sorted(native_dir.glob('r??_c??.png'))
    for p in natives:
        r = read(str(p) + '.generation.json')
        assert sha(p) == r['sha256']
        with Image.open(p) as im: im.load(); assert im.size == (1254, 1254)
    count = len(entries)
    baseline = sum(e.get('baseline', False) for e in entries)
    active_incomplete = int(active not in complete)
    timestamp = now()
    state = {'appearance': 'donghai_lantern', 'title': '05 渔村元宵地图',
        'updatedAtUtc': timestamp, 'targetCityPixels': [65536, 65536],
        'targetTiles': 256, 'targetTilePixels': [4096, 4096],
        'baselineCompletePixelCandidates': baseline, 'newCompletePixelCandidates': count-baseline,
        'completePixelCandidates': count, 'missingTiles': 256-count,
        'tilesWithNoCompletePixels': 256-count, 'tilesWithoutAnyCurrentProduction': 256-count-active_incomplete,
        'formalAccepted': 0, 'clientAccepted': False, 'wholeCityComplete': False,
        'runtimePublished': False, 'activeTile': active, 'nativePatchesSaved': len(natives),
        'nativePatchesRequiredForActiveTile': 16, 'fragmentsCountAsTiles': False,
        'phase': 'native_expansion_and_scoped_seam_repairs',
        'qaStatus': 'candidate_scope_only_not_whole_city_or_client_acceptance',
        'currentCandidateRegistry': str(REGISTRY), 'currentCandidates': entries,
        'nextAction': 'Finish identified seam repairs; continue exact day-geometry native festival conversion and review each complete tile.'}
    # Full candidate images only count after actual decoding and SHA verification.
    index = {'updatedAtUtc': timestamp, 'appearance': 'donghai_lantern',
        'targetTiles': 256, 'wholeCityComplete': False, 'runtimePublished': False,
        'currentCandidateRegistry': str(REGISTRY),
        'counts': {'existingCompletePixelCandidates': baseline, 'newCompletePixelCandidates': count-baseline,
            'completePixelCandidates': count, 'inProgress': active_incomplete,
            'missing': 256-count-active_incomplete, 'withoutCompletePixels': 256-count,
            'formalAccepted': 0, 'clientAccepted': 0}, 'tiles': []}
    for row in range(1,17):
        for col in range(1,17):
            tile = f'r{row:02}_c{col:02}'
            e = complete.get(tile)
            index['tiles'].append({'id': tile, 'globalRectXYWH': [(col-1)*4096,(row-1)*4096,4096,4096],
                'status': 'complete_pixel_candidate' if e else ('in_progress' if tile==active else 'missing'),
                'completePixelCandidate': bool(e), 'formalAccepted': False, 'clientAccepted': False,
                'sourceFile': e['file'] if e else None, 'actualSha256': e['sha256'] if e else None,
                'shaMatches': True if e else None, 'actualPixels': [4096,4096] if e else None,
                'fullDecode': bool(e), 'qaStatus': e['qaStatus'] if e else 'not_ready',
                'qaRecords': e.get('qaRecords',[]) if e else []})
    shown = entries + ([{'tile': active, 'partial': True}] if active_incomplete else [])
    preview = Image.new('RGB', (384*len(shown),544), (38,49,58))
    draw = ImageDraw.Draw(preview)
    refs = []
    for i,e in enumerate(shown):
        x = i*384
        draw.text((x+10,10),e['tile'] + (' / native fragments' if e.get('partial') else ' / 4096 candidate'),fill='white')
        if e.get('partial'):
            for p in natives:
                row,col = int(p.stem[1:3]),int(p.stem[5:7])
                with Image.open(p) as im: preview.paste(im.crop((115,115,1139,1139)).resize((96,96),Image.Resampling.LANCZOS),(x+(col-1)*96,36+(row-1)*96))
                refs.append({'file':str(p),'sha256':sha(p),'role':'native fragment, not a complete tile'})
        else:
            with Image.open(e['file']) as im: preview.paste(im.convert('RGB').resize((384,384),Image.Resampling.LANCZOS),(x,36))
            refs.append({'file':e['file'],'sha256':e['sha256'],'role':'current complete pixel candidate'})
    draw.text((12,438), f'Complete pixel candidates {count}/256 | Formal accepted 0/256 | Client acceptance pending',fill='white')
    draw.text((12,462), f'Active {active}: {len(natives)}/16 native fragments | {256-count} tiles lack complete current pixels',fill='white')
    draw.text((12,486), 'Downscaled placement preview only. Full city is incomplete; seam QA is recorded per candidate.',fill='white')
    preview.save(ROOT/'current-preview.png')
    write(ROOT/'current-preview.png.generation.json', {'file':str(ROOT/'current-preview.png'), 'sha256':sha(ROOT/'current-preview.png'),
        'operation':'downscaled placement preview of SHA-verified complete candidates and separately labelled fragments',
        'finalArt':False,'derivedFrom':refs,'registry':str(REGISTRY)})
    registry['updatedAtUtc']=timestamp
    write(REGISTRY,registry)
    write(ROOT/'current-selection.json', {'schemaVersion':2,'authoritativeRegistry':str(REGISTRY),
        'updatedAtUtc':timestamp,'candidates':entries,'activeTile':active,'wholeCityComplete':False,'formalAccepted':False})
    write(ROOT/'current-work.json',state); write(ROOT/'progress.json',state)
    write(ROOT/'audit/tile-index.json',index)
    (ROOT/'integration-delivery-status.txt').write_text(
        f'05 渔村元宵地图：完整像素候选 {count}/256；正式验收 0/256；客户端未验收。\n'
        f'当前扩展 {active}：原生片段 {len(natives)}/16；尚无完整像素图块 {256-count} 张。\n'
        '候选、SHA 和检查范围以 current-candidates.json 为准；current-preview.png 仅为缩略总览。\n', encoding='utf-8')
    return {k:state[k] for k in ('completePixelCandidates','missingTiles','activeTile','nativePatchesSaved','formalAccepted')}

def select(tile,path,expected,qa,records):
    p = Path(path).resolve(); assert p.is_relative_to(ROOT)
    registry=read(REGISTRY) if REGISTRY.exists() else initial()
    previous=next((e for e in registry['candidates'] if e['tile']==tile),None)
    entry={'tile':tile,'file':str(p),'sha256':expected,'completePixelCandidate':True,
        'baseline': previous.get('baseline',False) if previous else False,
        'qaStatus':qa,'qaRecords':records,'formalAccepted':False,'clientAccepted':False}
    if previous: entry['previousSelectionEvidence']={'file':previous['file'],'sha256':previous['sha256']}
    verify(entry)
    registry['candidates']=[e for e in registry['candidates'] if e['tile']!=tile]+[entry]
    write(REGISTRY,registry)
    return status()

if __name__=='__main__':
    if sys.argv[1]=='select': result=select(*sys.argv[2:6],sys.argv[6:])
    elif sys.argv[1]=='status': result=status()
    else: raise SystemExit('select TILE FILE SHA QA_STATUS [QA_JSON ...] | status')
    print(json.dumps(result,ensure_ascii=False))
