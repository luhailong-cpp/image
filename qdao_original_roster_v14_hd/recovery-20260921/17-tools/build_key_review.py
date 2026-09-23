"""Composite four existing key-frame exports for review; never modifies action PNGs."""
import argparse, json
from PIL import Image, ImageDraw
from common import *

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--direction', choices=('W', 'NW'), required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--attempt', action='append', required=True)
    args = parser.parse_args()
    require(len(args.attempt) == 4, 'Supply exactly four attempts in phase01/05/09/13 order')
    out = RECOVERY / '17-delivery-preview' / 'key-review' / args.revision / args.direction
    require(not out.exists(), 'Keep previous key review; use a fresh revision')
    rows = []
    for frame, attempt in zip((1, 5, 9, 13), args.attempt):
        require(re.fullmatch(r'[A-Za-z0-9_-]+', attempt), 'Invalid attempt')
        path = HERE / 'staging' / attempt / 'candidate' / CHAR / 'walk' / args.direction / f'{frame:02d}.png'
        require(path.is_file(), 'Missing actual key frame: ' + str(path))
        rows.append({'frame': frame, 'attempt': attempt, 'path': str(path), 'sha256': sha(path)})
    out.mkdir(parents=True)
    for mode, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
        canvas = Image.new('RGB', (2048, 568), color)
        draw = ImageDraw.Draw(canvas)
        for index, row in enumerate(rows):
            with Image.open(row['path']) as image:
                small = image.resize((512, 512), Image.Resampling.LANCZOS)
            canvas.paste(small, (index * 512, 50), small)
            draw.text((index * 512 + 10, 12), row['attempt'], fill='white' if mode == 'dark' else 'black')
        destination = out / (mode + '.png')
        canvas.save(destination)
        save_new(destination.with_suffix('.png.generation.json'), {**image_identity(destination), 'route': 'derived-no-generation',
            'derivedFrom': rows, 'operation': 'review-only four-frame compositing at half display size; source PNG bytes untouched',
            'generationCalls': 0, 'visualApproval': False})
    save_new(out / 'sources.json', {'character_id': CHAR, 'direction': args.direction, 'sources': rows,
        'visual_review': 'pending', 'warning': 'Static four-key comparison only; no full cycle acceptance.'})
    print(json.dumps({'review': str(out), 'visual_review': 'pending'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
