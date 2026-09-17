"""Independent exact-source reconstruction, without using candidate rendering code."""
from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np
R=Path(r'E:\work\image\qdao_chibi_roster_v12');B=R/'review/27_ranger_natural_fixes';C=R/'candidate-stable-body/27_ink_kite_ranger'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
for d in ['N','E','SE','S','SW','W']:
 f=B/'six-direction-gait'/d/'final-sheet.png';m=json.loads(f.with_suffix('.assembly.json').read_text(encoding='utf-8-sig'));assert sha(f)==m['output_sha256'];im=Image.open(f).convert('RGBA')
 for rec in m['frames']:
  got=im.crop(rec['target_box'])
  if rec['replacement']:
   raw=Path(rec['raw_path']);assert sha(raw)==rec['raw_sha256'];assert sha(rec['builtin_original_path'])==rec['builtin_original_sha256'];assert sha(rec['prompt_path'])==rec['prompt_sha256'];mode='RGBA' if d=='S' else 'RGB';expected=Image.open(raw).convert(mode).crop(rec['raw_source_box']).resize((443,443),Image.Resampling.LANCZOS).convert('RGBA')
   if d=='S':
    ar=np.array(expected);ar[:,:,3][ar[:,:,3]<=3]=0;expected=Image.fromarray(ar)
  else:
   old=Path(rec['upstream_cell_path']);assert sha(old)==rec['upstream_cell_sha256'];expected=Image.open(old).convert('RGBA')
  assert got.tobytes()==expected.tobytes(),(d,rec['output_phase']);checks.append({'direction':d,'phase':rec['output_phase'],'replacement':rec['replacement'],'exact_native_reconstruction':True})
for d in ['NE','NW']:
 f=C/'source'/f'walk-{d}-final.png';m=json.loads(f.with_suffix('.assembly.json').read_text());assert sha(f)==m['output_sha256'];im=Image.open(f).convert('RGBA')
 for rec in m['source_cells']:
  s=Path(rec['source']);assert sha(s)==rec['sha256'];raw=Image.open(s).convert('RGBA')
  if rec['full_cell_resolution_normalization']:raw=raw.resize(tuple(rec['normalized_sheet_size']),Image.Resampling.LANCZOS)
  expected=raw.crop(rec['normalized_cell_box']);got=im.crop(rec['normalized_cell_box']);assert expected.tobytes()==got.tobytes(),(d,rec['output_phase']);checks.append({'direction':d,'phase':rec['output_phase'],'replacement':not rec['preserved_original'],'exact_native_reconstruction':True})
assert len(checks)==64 and sum(x['replacement'] for x in checks)==37
out={'status':'passed','walk_frames':64,'authored_replacements':37,'unchanged_source_cells':27,'exact_reconstruction_passed':64,'new_pose_pixels_painted_by_script':False,'notes':'S new cells preserve generated RGB and all alpha>3; alpha<=3 background noise only is cleared; other six-direction edits retain their originally recorded RGB full-cell normalization. NE03 original cell remains pixel exact.','checks':checks}
(B/'final-source-reconstruction.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
