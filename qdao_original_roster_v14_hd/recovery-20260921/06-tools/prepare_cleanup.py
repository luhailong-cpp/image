"""Prepare exact 06-only cleanup inventories and preserve source evidence as text."""
from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;REC=HERE.parent;ROOT=REC.parent.parent;FINAL=REC/'06-final';CHAR='06_thunder_caster_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(v):
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k not in ('image_url','base64','b64_json','data')}
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,str) and v.startswith('data:image/'):return '[image payload removed; textual output and hashes retained]'
 return v
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert (FINAL/'verification.json').exists()
scopes=[REC/'06-generation',REC/'06-work',REC/'06-work-SE-SW',HERE,REC/'06-audit',ROOT/'qdao_original_roster_v14_hd/generation'/CHAR,ROOT/'qdao_original_roster_v14_hd/candidate'/CHAR,ROOT/'qdao_original_roster_v13/generation'/CHAR,*[ROOT/'qdao_original_roster_v13/candidate'/CHAR/p for p in ['source','processing','review']]]
records=[];files=[];host={};known_raw_hashes=set()
for folder in scopes:
 folder=folder.resolve();assert folder.is_relative_to(ROOT.resolve()) and (folder.name.startswith('06') or CHAR in folder.parts)
 if not folder.exists():continue
 for p in sorted(folder.rglob('*')):
  if not p.is_file():continue
  digest=sha(p)
  files.append({'path':str(p),'sha256':digest,'bytes':p.stat().st_size})
  if p.name=='raw.png':known_raw_hashes.add(digest)
  if p.suffix.lower() in ('.json','.txt','.md'):
   try: txt=p.read_text(encoding='utf-8-sig')
   except UnicodeError:continue
   if p.suffix=='.json':
    try: value=clean(json.loads(txt))
    except json.JSONDecodeError:value=txt
   else:value=txt
   records.append({'historical_path':str(p),'historical_sha256':digest,'content':value})
   # Read exact tool-output paths, never enumerate or delete unrelated host assets.
   normalized=txt.replace('\\\\','\\')
   for s in re.findall(r'C:\\Users\\Administrator\\\.codex\\generated_images\\[^\r\n"<>]+?\.png',normalized):
    hp=Path(s)
    if hp.exists():host[str(hp.resolve())]={'path':str(hp.resolve()),'sha256':sha(hp),'bytes':hp.stat().st_size}
host_files=[r for r in host.values() if r['sha256'] in known_raw_hashes]
write(FINAL/'provenance/production-text-records.json',records)
plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'authorization':'User delegated retention choice after explicitly permitting deletion. Keep final game art/design/preview and textual provenance; delete raw/reject/rollback/intermediate assets only after verification.','workspace_root':str(ROOT.resolve()),'directories':[str(p.resolve()) for p in scopes if p.exists()],'files':files,'file_count':len(files),'bytes':sum(r['bytes'] for r in files),'host_generated_image_files':host_files,'protected_final_directory':str(FINAL.resolve()),'protected_existing_selected_old_assets':'qdao_original_roster_v13/candidate/06_thunder_caster_boy/walk/S and idle; exact original bytes retained for compatibility','protected_designs':['q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png','qdao_original_roster_v13/candidate/06_thunder_caster_boy/portrait.png','qdao_original_roster_v13/references/06_thunder_caster_boy']}
write(FINAL/'cleanup-plan.json',plan)
print(json.dumps({'files':len(files),'MiB':round(plan['bytes']/1048576,1),'host_files':len(host_files),'text_records':len(records)}))
