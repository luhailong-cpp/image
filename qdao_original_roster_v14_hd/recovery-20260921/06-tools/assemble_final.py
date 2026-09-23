"""Assemble explicit, hash-pinned 06 delivery and self-contained textual provenance."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,argparse
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
REC=HERE.parent
ROOT=REC.parent.parent
CHAR='06_thunder_caster_boy'
DIRS=['N','NE','E','SE','S','SW','W','NW']
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def clean(v):
 if isinstance(v,dict): return {k:clean(x) for k,x in v.items() if k not in ('image_url','data','base64','b64_json')}
 if isinstance(v,list): return [clean(x) for x in v]
 return v
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--restored',action='store_true');parser.add_argument('--revision');args=parser.parse_args()
 sources={'E':REC/'06-work','N':HERE/'work-N-NE','NE':HERE/'work-NE-final','SE':HERE/'work-SE-SW','SW':HERE/'work-SE-SW','W':HERE/'work-W-NW','NW':HERE/'work-W-NW'}
 overrides={}
 for d,base in sources.items():
  origin=base/'candidate'/CHAR
  records=read(origin/'processing/frame-sources.json')
  for n in range(1,17):
   key=f'walk/{d}/{n:02}.png';p=origin/key;r=records[key]
   overrides[key]={'path':str(p.resolve()),'sha256':sha(p),'selected_revision':Path(r['source']['path']).parent.name,'visual_status':'root_selected_unapproved'}
 if args.restored:
  for d,first,last,base in [('S',1,8,'work-S-first-final'),('S',9,16,'work-S-second-final')]:
   origin=HERE/base/'candidate'/CHAR;records=read(origin/'processing/frame-sources.json')
   for n in range(first,last+1):
    key=f'walk/{d}/{n:02}.png';p=origin/key;r=records[key]
    overrides[key]={'path':str(p.resolve()),'sha256':sha(p),'selected_revision':Path(r['source']['path']).parent.name,'visual_status':'root_selected_unapproved'}
  origin=HERE/'work-idle-final/candidate'/CHAR;records=read(origin/'processing/frame-sources.json')
  for d in DIRS:
   key=f'idle/{d}.png';p=origin/key;r=records[key]
   overrides[key]={'path':str(p.resolve()),'sha256':sha(p),'selected_revision':Path(r['source']['path']).parent.name,'visual_status':'root_selected_unapproved'}
 revision=args.revision or ('complete-restored-v2' if args.restored else 'complete-review-v1')
 selection=HERE/('selections-restored-final.json' if args.restored else 'selections-final-review.json')
 write(selection,{'overrides':overrides})
 subprocess.run([sys.executable,str(HERE/'build_package.py'),'--revision',revision,'--selections',str(selection)]+(['--allow-legacy-restoration'] if args.restored else []),check=True)
 subprocess.run([sys.executable,str(HERE/'audit_snapshot.py'),'--revision',revision],check=True)
 snapshot=HERE/'revisions'/revision
 final=REC/'06-final'
 assert args.restored or not final.exists()
 shutil.copytree(snapshot,final,dirs_exist_ok=args.restored)
 m=read(final/'manifest.json');assert m['actual_walk']==128 and m['actual_idle']==8 and not m['missing']
 archive_by_hash={}
 for folder in [REC/'06-generation',ROOT/'qdao_original_roster_v14_hd/generation'/CHAR]:
  for p in folder.glob('*/raw.png'):
   archive_by_hash.setdefault(sha(p),[]).append(p.parent)
 provenance=[]
 for r in m['files']:
  p=Path(r['source']);origin=next(x for x in p.parents if x.name==CHAR)
  record=r.get('source_record');item={'final_path':'runtime/'+r['path'],'final_sha256':r['sha256'],'final_size':r['size'],'selected_revision':r['selected_revision'],'historical_source_path':r['source'],'processing_record':record,'source_images_retained':True,'raw_retention_decision':'remove only after final verification, user delegated choice 2026-09-23','text_records':[]}
  dirs=[]
  if record:
   raw=origin/record['source']['path']
   assert sha(raw)==record['source']['sha256']
   dirs.append(raw.parent)
   dirs+=archive_by_hash.get(record['source']['sha256'],[])
  for folder in dict.fromkeys(dirs):
   for f in sorted(folder.iterdir()):
    if f.is_file() and f.suffix in ('.json','.txt','.md'):
     content=read(f) if f.suffix=='.json' else f.read_text(encoding='utf-8-sig')
     item['text_records'].append({'historical_path':str(f),'historical_sha256':sha(f),'content':clean(content)})
  derived=p.with_name(p.name+'.generation.json')
  if derived.exists(): item['derived_image_record']=read(derived)
  if args.restored and (r['path'].startswith('walk/S/') or r['path'].startswith('idle/')):
   old=ROOT/'qdao_original_roster_v13/candidate'/CHAR/r['path']
   item['legacy_restoration_reference']={'path':str(old),'sha256':sha(old),'size':[512,512],'original_file_preserved_byte_exact':True,'final_operation':'AI edge restoration/redraw of existing pose; not a raster upscale and not a new invented walk slot'}
  provenance.append(item)
  for k in ['source_record','source_record_file','source_record_file_sha256']:
   r.pop(k,None)
  r['historical_source_path']=r.pop('source')
  r['source']='runtime/'+r['path']
  r['provenance_record']='provenance/selected-sources.json#'+r['path']
 write(final/'provenance/selected-sources.json',provenance)
 shutil.copy2(REC/'06-current-source-audit/old-byte-baseline.json',final/'provenance/preserved-old-byte-baseline.json')
 m['schema']='qdao-06-final-offline-delivery-v1'
 m['revision']='06-final-restored-20260923' if args.restored else '06-final-20260923'
 m['legacy_final_copies_ai_restored']=args.restored
 if args.restored:
  m['restored_legacy_action_count']=24
  m['all_runtime_actions_size']=[1024,1024]
  m['old_action_protection']='Original 24 V13 512px PNG files remain byte-exact at original paths. Final runtime selects new AI edge-restored 1024px exports.'
 m['source_image_retention']='Present during assembly; remove after final verification per user-delegated final-only policy. Self-contained textual provenance retained.'
 m['selected_provenance_sha256']=sha(final/'provenance/selected-sources.json')
 m['portrait_design']={'path':'../../../q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png','sha256':sha(ROOT/'q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png')}
 write(final/'manifest.json',m)
 # This page is provisional until root's review is recorded. All imagery is local to final.
 template=(HERE/'preview-template.html').read_text(encoding='utf-8')
 (final/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(m,ensure_ascii=False)),encoding='utf-8')
 print(json.dumps({'final':str(final),'walk':128,'idle':8,'provenance_entries':len(provenance),'manifest_sha256':sha(final/'manifest.json')}))
if __name__=='__main__':main()
