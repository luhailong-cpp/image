"""Audit preserved slots, actual native raw sizes, unique sources and exact pixel mirrors."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CHAR='04_mountain_guardian_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(im):return hashlib.sha256(im.tobytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--revision',required=True);args=parser.parse_args()
out=(HERE/'revisions'/args.revision).resolve();assert out.is_relative_to(HERE)
manifest_path=out/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
rows=manifest['files'];assert len(rows)==136 and manifest['actual_walk']==128 and manifest['actual_idle']==8
bykey={r['path']:r for r in rows};assert len(bykey)==136
oldroot=ROOT.parent/'qdao_original_roster_v13/candidate'/CHAR
oldfiles=[*[p for p in oldroot.glob('walk/*/*.png') if p.stem.isdigit() and 1<=int(p.stem)<=16],*[p for p in oldroot.glob('idle/*.png') if p.stem in ('N','NE','E','SE','S','SW','W','NW')]]
for p in oldfiles:
 key=p.relative_to(oldroot).as_posix();row=bykey[key]
 assert row['selected_revision']=='preserved-v13' and row['sha256']==sha(p)==sha(out/'runtime'/key)
new=[];raw_hashes=[];raw_pixel_hashes=[];raw_mirror_hashes=[]
for row in rows:
 if row['selected_revision']=='preserved-v13':continue
 assert row['size']==[1024,1024]
 record=row['source_record'];source=record['source'];origin=Path(row['source_record_file']).parent.parent
 raw=origin/source['path'];im=Image.open(raw);size=list(im.size)
 assert sha(raw)==source['sha256'] and size==source['native_size'] and min(size)>=1024
 assert source['grid']==[1,1] and source['cell_index']==0 and source['selected_source_cell_indices']==[0]
 assert source['output_frame_map']==[int(Path(row['path']).stem)] and record['output_sha256']==row['sha256']
 raw_hashes.append(sha(raw));rgba=im.convert('RGBA');raw_pixel_hashes.append(pixels(rgba));raw_mirror_hashes.append(pixels(rgba.transpose(Image.Transpose.FLIP_LEFT_RIGHT)))
 new.append({'path':row['path'],'raw_path':str(raw),'raw_sha256':sha(raw),'native_size':size,'grid':source['grid'],'output_size':row['size'],'selected_revision':row['selected_revision']})
assert len(new)==24 and len(set(raw_hashes))==24 and len(set(raw_pixel_hashes))==24
assert not (set(raw_pixel_hashes)&set(raw_mirror_hashes)), 'Exact horizontal raw mirror found'
assert len({r['sha256'] for r in rows})==136
output_pixels=[];output_mirror_pixels=[]
for row in rows:
 im=Image.open(out/'runtime'/row['path']).convert('RGBA')
 # Crop to alpha bounds so a mere canvas translation cannot conceal an exact duplicate or mirror.
 im=im.crop(im.getchannel('A').getbbox());output_pixels.append((im.size,pixels(im)));output_mirror_pixels.append((im.size,pixels(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT))))
assert len(set(output_pixels))==136 and not (set(output_pixels)&set(output_mirror_pixels))
v2=HERE/'revisions/review-set-v2/manifest.json'
diff=[]
if v2.exists():
 before={r['path']:r for r in json.loads(v2.read_text(encoding='utf-8'))['files']}
 diff=[r['path'] for r in rows if r['sha256']!=before[r['path']]['sha256']]
 if args.revision=='review-set-v3':assert diff==['walk/NW/15.png']
report={'revision':args.revision,'manifest_sha256':sha(manifest_path),'walk_count':128,'independent_idle_count':8,'preserved_v13_actions':len(oldfiles),'preserved_v13_walk':sum(p.parent.parent.name=='walk' for p in oldfiles),'preserved_v13_idle':sum(p.parent.name=='idle' for p in oldfiles),'preserved_bytes_match':True,'new_walk_count':24,'new_native_raw_sizes_at_least_1024':True,'new_output_sizes_1024':True,'unique_new_raw_byte_hashes':len(set(raw_hashes)),'unique_new_raw_pixel_hashes':len(set(raw_pixel_hashes)),'unique_output_byte_hashes':136,'unique_output_alpha_cropped_pixel_hashes':136,'exact_horizontal_raw_or_output_mirror_pairs':0,'new_native_single_source_grid_1x1':True,'changed_png_slots_vs_review_set_v2':diff,'scope_limits':'File/pixel/source checks establish no exact duplicate, exact horizontal mirror, or raw-cell reuse among new slots. Semantic gait distinctness and generated pose authenticity require provenance plus visual review; this report is not art approval. Preserved old action sources are not recertified as new1024 assets.','new_sources':new,'formal_approval':False,'browser_dynamic_review':False}
(out/'action-scope-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('new_sources','scope_limits')},ensure_ascii=False))
