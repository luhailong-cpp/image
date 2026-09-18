from pathlib import Path
import sys,json,hashlib,shutil,datetime
record=json.loads(sys.stdin.read())
folder=Path('E:/work/image/qdao_original_roster_v13/generation/06_thunder_caster_boy')
name=record['batch_name'];src=Path(record['original_generated_path']);dst=folder/(name+'-raw.png')
assert name and all(c.isalnum() or c in '_-' for c in name)
if dst.exists():
 assert hashlib.sha256(src.read_bytes()).hexdigest()==hashlib.sha256(dst.read_bytes()).hexdigest(),'Preserve earlier different generation as another version'
else:shutil.copy2(src,dst)
prompt=folder/(name+'-prompt.txt')
record.update({'saved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'saved_raw_path':str(dst),'raw_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'prompt_file':prompt.name,'prompt_sha256':hashlib.sha256(prompt.read_bytes()).hexdigest(),'image_payload_preservation':'Actual native PNG copied unchanged; full data URI omitted from this text receipt because it contains these same image bytes.'})
(folder/(name+'-tool-result.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'raw':str(dst),'sha256':record['raw_sha256']}))

