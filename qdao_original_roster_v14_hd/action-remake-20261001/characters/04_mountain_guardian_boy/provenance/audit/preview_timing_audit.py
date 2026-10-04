"""Read-only GIF timing and provenance audit; outputs text JSON here only."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from PIL import Image, ImageSequence
import hashlib, json, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for p in sorted((ROOT/'preview').glob('*.gif')):
    row={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'errors':[],'staleSources':[]}
    with Image.open(p) as im:
        row['frameCount']=im.n_frames
        row['durationsMs']=[frame.info.get('duration',0) for frame in ImageSequence.Iterator(im)]
    row['durationMs']=sum(row['durationsMs'])
    side=p.with_name(p.name+'.generation.json')
    if not side.exists(): row['errors'].append('missing_sidecar')
    else:
        j=json.loads(side.read_text(encoding='utf-8-sig')); op=j.get('operation',{})
        row['declaredDurationMs']=op.get('sequenceDurationMs')
        row['timingStatus']=op.get('timingStatus')
        if j.get('sha256')!=row['sha256']: row['errors'].append('gif_sha_mismatch')
        if op.get('durationsMs')!=row['durationsMs']: row['errors'].append('gif_frame_duration_mismatch')
        if row['declaredDurationMs']!=row['durationMs']: row['errors'].append('gif_total_duration_mismatch')
        for source in j.get('derivedFrom',[]):
            q=ROOT/source['path']
            if not q.exists() or sha(q)!=source.get('sha256'): row['staleSources'].append(source['path'])
    rows.append(row)
report={'completedAt':datetime.now(timezone.utc).isoformat(),'scope':'GIF实际时长/sidecar/当前来源只读核对；不包含动态观感验收。','gifs':rows,
    'summary':{'count':len(rows),'errorCount':sum(len(r['errors']) for r in rows),'staleSourceGifCount':sum(bool(r['staleSources']) for r in rows),
               'durationCounts':dict(Counter(str(r['durationMs']) for r in rows))}}
(OUT/'preview_timing_audit_20261003.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'summary':report['summary'],'issues':[r for r in rows if r['errors'] or r['staleSources']],
    'runNormalVariants':[{k:r[k] for k in ['file','durationMs','timingStatus']} for r in rows if r['file'].endswith('_normal.gif') and '/run_' in r['file']]},ensure_ascii=False,indent=2))
