"""Lay out reviewed native ImageGen frames; never invent or warp a pose.

This is an input provenance helper, not a change to the frozen image processor.
All source boxes are whole generated single-frame canvases or original grid cells.
No alpha/bbox fitting, body-part edits, mirroring, rotation or independent body fit.
"""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json

PACK = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local(value):
    path = (PACK / value).resolve()
    if not path.is_relative_to(PACK):
        raise ValueError('Path leaves the repair batch')
    return path

def rel(path):
    return path.relative_to(PACK).as_posix()

def assemble(spec_path):
    spec_path = spec_path.resolve()
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    direction = spec['direction']
    if direction not in ('NW', 'NE', 'SE', 'SW'):
        raise ValueError('Only the explicitly reviewed diagonal sources are eligible')
    frames = spec['frames']
    if len(frames) != 4 or [f['frame'] for f in frames] != [1,2,3,4]:
        raise ValueError('Require four real frames in exact phase order')
    cell = 627
    sheet = Image.new('RGB', (cell*2, cell*2), (255,0,255))
    lineage, artifacts = [], {}
    for entry in frames:
        src, prompt = local(entry['raw_source']), local(entry['prompt_file'])
        if entry.get('visual_status') != 'passed_single_pose_review':
            raise ValueError('Do not assemble an unreviewed pose')
        if sha(src) != entry['raw_sha256'] or sha(prompt) != entry['prompt_sha256']:
            raise ValueError('Input or prompt changed since review')
        im = Image.open(src)
        if im.mode not in ('RGB', 'RGBA') or (im.mode == 'RGBA' and im.getextrema()[3] != (255,255)):
            raise ValueError('Expected opaque magenta-backed native raw')
        box = entry['source_box']
        left, top, right, bottom = box
        if not (0 <= left < right <= im.width and 0 <= top < bottom <= im.height):
            raise ValueError('Invalid source cell')
        width, height = right-left, bottom-top
        if width != height:
            raise ValueError('Whole canvas/cell resampling must stay isotropic')
        if list(box) != [0,0,im.width,im.height]:
            if im.width != im.height or im.width % 2 or width != im.width//2:
                raise ValueError('Partial body crops are prohibited: use exact native grid cell')
            if left not in (0,width) or top not in (0,height):
                raise ValueError('Source crop is not a native 2x2 grid cell')
        tile = im.crop(box).convert('RGB')
        if tile.size != (cell,cell):
            tile = tile.resize((cell,cell), Image.Resampling.LANCZOS)
        i = entry['frame']-1
        x,y = i%2*cell,i//2*cell
        sheet.paste(tile,(x,y))
        source_entry = dict(entry)
        source_entry.update(raw_source=rel(src),raw_native_size=list(im.size),whole_canvas_scale=cell/width,target_box=[x,y,x+cell,y+cell],prompt_file=rel(prompt))
        lineage.append(source_entry)
        artifacts[rel(src)] = {'path':rel(src),'sha256':sha(src),'native_size':list(im.size),'prompt_file':rel(prompt),'prompt_sha256':sha(prompt),'source_type':'native_imagegen_output'}
    out = PACK / f'sources/walk_{direction}_2x2.png'
    if out.exists():
        raise FileExistsError('Never silently overwrite an accepted processing input')
    sheet.save(out)
    record = {'direction':direction,'path':rel(out),'sha256':sha(out),'native_size':list(sheet.size),'source':'deterministic layout of independently reviewed native built-in image_gen frames','source_type':'assembled_2x2_from_native_generations','assembled':True,'native_generation_count':len(artifacts),'generation_lineage':{'operation':'crop_native_cells_and_uniformly_resample_whole_canvases_then_layout','body_warp_or_per_frame_bbox_fit':False,'spec_file':rel(spec_path),'spec_sha256':sha(spec_path),'assembler_sha256':sha(Path(__file__)),'frames':lineage,'raw_artifacts':list(artifacts.values())}}
    sidecar = PACK / f'sources/walk_{direction}_2x2.lineage.json'
    sidecar.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('spec',type=Path)
    args = ap.parse_args()
    assemble(args.spec)
