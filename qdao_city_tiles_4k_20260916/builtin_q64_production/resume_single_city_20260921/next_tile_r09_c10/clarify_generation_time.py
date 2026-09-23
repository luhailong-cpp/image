from pathlib import Path
import sys,json,hashlib,shutil
P=Path(__file__).resolve().parent;Q=P/'repairs/versions'/sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
g=Q/'repair-native-1254.png.generation.json';r=Q/'repair.json'
for p in (g,r):
    backup=p.with_name(p.name+'.before-timestamp-clarification.json');assert not backup.exists();shutil.copyfile(p,backup)
d=json.loads(g.read_text(encoding='utf-8'));d['generatedAtMeaning']='Host-observed tool completion time, not disclosed server generation timestamp';d['observedCompletionAt']=d['generatedAt'];d['serverGenerationTimestamp']=None
g.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
d=json.loads(r.read_text(encoding='utf-8'));d['generationRecord']['sha256']=sha(g)
for f in ['sourceCandidate','sourceRecord']:
    d[f]['file']=str(Path(d[f]['file']).resolve())
d['recordClarification']='Generation time explicitly labeled host-observed tool completion; original pre-clarification records preserved alongside.'
r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'record':str(r),'sha256':sha(r),'generationRecordSha256':sha(g)}))
