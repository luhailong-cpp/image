from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parent
PARALLEL = ROOT.parent
PROJECT = Path('D:/work/image')
REPAIR = PARALLEL / 'parent_repairs_20261008' / 'west-upper'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp = lambda: datetime.now(timezone.utc).isoformat()

progress_path = PARALLEL / 'tianyong_festival/progress.json'
progress = json.loads(progress_path.read_text(encoding='utf-8-sig'))
selection_path = Path(progress['candidateSet'])
selection = json.loads(selection_path.read_text(encoding='utf-8-sig'))
items = []
for entry in selection['candidates']:
    path = Path(entry['file'])
    before = sha(path)
    with Image.open(path) as im:
        im.load()
        size, mode = im.size, im.mode
        alpha = im.getchannel('A').getextrema() if 'A' in im.getbands() else (255, 255)
        hist = im.getchannel('A').histogram() if 'A' in im.getbands() else None
    tile = entry.get('tile', 'r08_c10' if 'fragment' in path.name else path.stem)
    is_fragment = 'fragment' in path.name or alpha[0] != 255
    items.append(dict(appearance='tianyong_festival', tileId=tile, path=str(path),
        sha256=before, selectionShaMatches=before==entry.get('sha256'),
        width=size[0], height=size[1], mode=mode, alphaRange=alpha,
        opaquePixels=hist[255] if hist else size[0]*size[1],
        nonzeroAlphaPixels=sum(hist[1:]) if hist else size[0]*size[1],
        fullPixelCandidate=size==(4096,4096) and not is_fragment,
        fragment=is_fragment, selectionSource=str(selection_path),
        generationRecord=entry.get('generationRecord'),
        qaEvidence=entry.get('selectionRecord'), issue=entry.get('remainingLimitations', []),
        stableDuringRead=before==sha(path), formalAccepted=False))
(ROOT/'tianyong').mkdir(parents=True, exist_ok=True)
(ROOT/'tianyong/audit.json').write_text(json.dumps(dict(observedAt=stamp(),
    selectionSource=str(selection_path), selectionSha256=sha(selection_path),
    progressSource=str(progress_path), entries=items,
    counts=dict(fullPixelCandidates=sum(i['fullPixelCandidate'] for i in items),
                fragments=sum(i['fragment'] for i in items), formalAccepted=0, wholeCityComplete=False)),
    ensure_ascii=False, indent=2), encoding='utf-8')

# Disjoint parent repair: the city worker is expanding c10. Never edit its selection.
REPAIR.mkdir(parents=True, exist_ok=True)
pair = {i['tileId']:i for i in items if i['tileId'] in ['r08_c07','r08_c08']}
assert len(pair)==2 and all(i['selectionShaMatches'] and i['stableDuringRead'] for i in pair.values())
context = Image.new('RGB', (1254,1254))
parts = []
for tile, srcbox, dst in [('r08_c07',(3469,480,4096,1734),(0,0)),
                          ('r08_c08',(0,480,627,1734),(627,0))]:
    with Image.open(pair[tile]['path']) as im: context.paste(im.crop(srcbox).convert('RGB'),dst)
    parts.append(dict(tile=tile, source=pair[tile], cropLTRB=srcbox, pasteXY=dst))
context_path = REPAIR/'context.png'
context.save(context_path)
(REPAIR/'context.png.generation.json').write_text(json.dumps(dict(file=str(context_path),
    sha256=sha(context_path), createdAt=stamp(), operation='Two adjacent native crops concatenated; no resizing, repainting or tone changes.',
    tileLocalWindowLTRB=[3469,480,4723,1734], coordinatesRelativeTo='r08_c07 top left',
    parts=parts),ensure_ascii=False,indent=2),encoding='utf-8')
(REPAIR/'config.snapshot.json').write_text((PROJECT/'config/image-generation.json').read_text(encoding='utf-8-sig'),encoding='utf-8')
(REPAIR/'model-verification.json').write_text(json.dumps(dict(checkedAt=stamp(),
    url='https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst',
    confirmedTarget='gpt-image-2.5-sunburst', confirmedHighestQuality='max',
    userChosenRoute='builtin', actualModel=None, actualQuality=None,
    note='Read official model page on 2026-10-08; builtin tool exposes no model or quality parameter. Existing batch configuration retained.'),indent=2),encoding='utf-8')
print(json.dumps(dict(audit=str(ROOT/'tianyong/audit.json'),counts={'complete':sum(i['fullPixelCandidate'] for i in items),'partial':sum(i['fragment'] for i in items)},repairContext=str(context_path))))
