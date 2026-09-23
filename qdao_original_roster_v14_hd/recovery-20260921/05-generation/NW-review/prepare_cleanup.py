from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
GEN=Path(__file__).resolve().parent.parent
ROOT=GEN.parents[2]
n=int(sys.argv[1]);v=int(sys.argv[2]);oldv=int(sys.argv[3])
arc=GEN/f'NW{n:02d}-single-v{v}';arc.mkdir(exist_ok=True)
assert not (arc/'raw.png').exists()
refs=[GEN/f'NW{n:02d}-single-v{oldv}'/'raw.png',ROOT/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/idle/NW.png',ROOT/'designs/jubaozhai-ui/02-characters.png']
assert all(r.exists() for r in refs)
prompt=f'''Use case: background-extraction EDIT. Clean ONE existing NW{n:02d} walking frame, IMAGE1, of this celestial musician girl. This is only removal of disconnected background debris. Preserve the precise existing full-body pose and all character pixels as closely as possible, including both legs, two boot positions and support, rear-left NW camera, head, crown, long purple hair, robe, gold embroidery, instrument and ribbons. Do NOT change the walking phase, facial direction, size, proportions or clothes.
Remove ALL isolated small purple, grey or colored specks floating OUTSIDE the character silhouette, including the tiny detached purple speck in the empty space to the right of the skirt BELOW the ribbon tips. Background must be genuinely transparent with clean antialiased edges. Preserve every real purple hair/clothing detail and translucent lavender ribbon. Do not erase actual costume or grow additional objects.
Image1 is the exact edit target; Image2 locks the original rear-left NW identity and camera; Image3 is the confirmed PRIMARY ART STYLE reference for finely painted clean bright rounded material. No UI. One full figure only. Keep native square1254x1254 or larger, minimum1024 each edge. Exact same framing as Image1. No shadows, background color, checkerboard, writing or labels.'''
req={'tool':'built-in image_gen','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8')),'actual_request':{'prompt':prompt,'referenced_image_paths':[r.as_posix() for r in refs],'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':r.as_posix(),'sha256':hashlib.sha256(r.read_bytes()).hexdigest()} for r in refs]}
(arc/'prompt.txt').write_bytes(prompt.encode())
(arc/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(arc)
