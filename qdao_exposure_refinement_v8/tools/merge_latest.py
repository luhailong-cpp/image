"""Merge a captured current source revision without overwriting concurrent art."""
import json
from pathlib import Path
from refine_library import V8, PROCESSING, classify, choose_path, write_json

def main():
    plan=json.loads(PROCESSING.read_text('utf8'))
    latest=json.loads((V8/'supplementary_inventory.json').read_text('utf8'))
    rows={r['path']:r for r in plan['records']};updated=0
    for a in latest['assets']:
        if a.get('error') or a.get('live_changed_after_capture'):raise RuntimeError(f'Unstable snapshot: {a["path"]}')
        prior=rows.get(a['path'])
        if prior and prior['original_sha256']==a['sha256']:continue
        preset,kind,reason=classify(a['path'])
        if Path(a['path']).name in ('title_character.png','title_pet.png'):
            preset,kind,reason='preserve','technical','Independent calligraphic label; preserve readable text brightness'
        history=list(prior.get('source_revision_history',[])) if prior else []
        if prior:history.append({k:prior[k] for k in ('original_sha256','output_sha256','backup','status')})
        rows[a['path']]=dict(path=a['path'],original_sha256=a['sha256'],output_sha256=a['sha256'],
            backup='backups/'+a['sha256']+a['extension'],changed=False,kind=kind,preset=preset,reason=reason,
            canonical_path=a['path'],protect_chroma=a.get('metrics',{}).get('magenta_chroma_fraction',0)>.03,
            classification=a['classification'],before_metrics=a.get('metrics'),expected_size=a['size'],expected_mode=a['mode'],
            source_snapshot_time=a['snapshot_time'],source_revision_history=history,status='planned')
        updated+=1
    groups={}
    for r in rows.values():groups.setdefault(r['original_sha256'],[]).append(r)
    for group in groups.values():
        canonical=choose_path([r['path'] for r in group]); chosen=next(r for r in group if r['path']==canonical)
        for r in group:
            r['canonical_path']=canonical
            r['preset']=chosen['preset'];r['kind']=chosen['kind'];r['reason']=chosen['reason']
    plan['records']=sorted(rows.values(),key=lambda r:r['path'])
    plan['status']='planned' if updated else plan['status']
    plan['latest_snapshot_time']=latest['snapshot_time']
    plan['latest_added_or_revised']=updated
    write_json(PROCESSING,plan)
    print(json.dumps({'updated':updated,'records':len(plan['records'])}))
if __name__=='__main__':main()
