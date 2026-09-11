from pathlib import Path
from PIL import Image
import hashlib,json,base64,re,datetime
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PACK=ROOT/'qdao_ui_style_recut_v10'
ST=PACK/'staged'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=[];svg_rows=[];portraits=[]
for e in read(PACK/'contracts/current_files.json')['files']:
 p=e['path'];a=ROOT/p;b=ST/p; row=dict(path=p,family=e['family'],production_sha256=sha(a),staged_sha256=sha(b))
 row['identical_bytes']=row['production_sha256']==row['staged_sha256']
 with Image.open(a) as ia,Image.open(b) as ib:
  row['size']=list(ia.size);row['canvas_matches']=ia.size==ib.size;row['mode_matches']=ia.mode==ib.mode
 files.append(row)
for rel in ['qdao_ui_redesign_v5/components/manifest.json','exact_qdao_slices/manifest_native_q5.json']:
 for e in read(ROOT/rel)['assets']:
  svg=(Path(rel).parent/e['svg']) if 'components/' in rel else Path(e['svg'])
  png=(Path(rel).parent/e['png']) if 'components/' in rel else Path(e['png'])
  a=ROOT/svg;b=ST/svg;actual=sha(a);encoded=re.search(r'data:image/png;base64,([^"\s]+)',a.read_text(encoding='utf-8-sig'))
  row=dict(path=svg.as_posix(),manifest=rel,production_sha256=actual,staged_sha256=sha(b),identical_to_staged=actual==sha(b),manifest_svg_sha_matches=e.get('svg_sha256')==actual,manifest_png_sha_matches=e.get('png_sha256')==sha(ROOT/png),embedded_png_matches=bool(encoded) and base64.b64decode(encoded.group(1))==(ROOT/png).read_bytes())
  svg_rows.append(row)
am='designs/attribute-panels/v2-painted/unity-slices/manifest.json'
mapped=read(PACK/'source-map.attributes.json')['outputs']
approved=read(OUT/'ui-portraits-final-review.json')['records']
for e in read(ROOT/am)['sprites']:
 if not e['name'].startswith('portrait_') or e['name']=='portrait_frame':continue
 name=e['name'];src=ROOT/e['source'];target=ROOT/Path(am).parent/'png'/f'{name}.png'
 source_sha=sha(src);outsha=sha(target);m=next(i for i in mapped if i['name']==name);s=next(i for i in read(ST/am)['sprites'] if i['name']==name);review=next(i for i in approved if i['name']==name+'.png')
 x,y,w,h=e['sourceRectNativeTopLeft'];rebuilt=Image.open(src).convert('RGBA').resize(tuple([e['width'],e['height']]),Image.Resampling.LANCZOS,box=(x,y,x+w,y+h))
 portraits.append(dict(name=name,path=target.relative_to(ROOT).as_posix(),source=e['source'],source_sha256=source_sha,production_sha256=outsha,approved_sha256=review['sha256'],matches_approved=outsha==review['sha256'],manifest_source_matches=e.get('sourceSha256')==source_sha,manifest_output_matches=e.get('sha256')==outsha,staged_manifest_source_matches=s.get('sourceSha256')==source_sha,staged_manifest_output_matches=s.get('sha256')==outsha,mapping_source_matches=m.get('sourceSha256')==source_sha,mapping_output_matches=m.get('outputSha256')==outsha,frozen_crop_exact=Image.open(target).convert('RGBA').tobytes()==rebuilt.tobytes()))
gen=read(PACK/'generation-status.json');validation=read(PACK/'validation.json')
report_files=[p.relative_to(PACK).as_posix() for p in PACK.glob('*.json') if any(t in p.name for t in ['publish','delivery'])]
changing=[e['path'] for e in files if sha(ROOT/e['path'])!=e['production_sha256'] or sha(ST/e['path'])!=e['staged_sha256']]
png_ok=all(e['identical_bytes'] and e['canvas_matches'] and e['mode_matches'] for e in files)
svg_ok=all(all(e[k] for k in ['identical_to_staged','manifest_svg_sha_matches','manifest_png_sha_matches','embedded_png_matches']) for e in svg_rows)
portraits_ok=all(all(v for k,v in e.items() if k.startswith(('matches_','manifest_','staged_manifest_','mapping_','frozen_'))) for e in portraits)
status='delivery_verified_status_record_pending' if png_ok and svg_ok and portraits_ok and not changing else 'incomplete_or_changed'
if png_ok and svg_ok and portraits_ok and not changing and gen.get('replaced_production_assets',0)>=155:status='delivery_verified'
result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=status,summary=dict(contract_pngs=len(files),png_byte_matches=sum(e['identical_bytes'] for e in files),svg_packages=len(svg_rows),svg_checks_passed=svg_ok,portraits_verified=portraits_ok,concurrent_changes=changing),generation_record=dict(status=gen.get('status'),generated_images=gen.get('generated_images'),replaced_production_assets=gen.get('replaced_production_assets'),next_step=gen.get('next_step')),producer_validation=dict(status=validation.get('status'),asset_count=validation.get('asset_count'),counts=validation.get('counts')),producer_publication_report_paths=report_files,files=files,svg_records=svg_rows,portraits=portraits,scope_note='Read-only asset and metadata verification. Does not assert Unity runtime integration.')
(OUT/'ui-final-delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['files','svg_records','portraits']},ensure_ascii=False))
