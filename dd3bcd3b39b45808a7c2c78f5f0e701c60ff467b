"""Hash-guarded, backed-up publication of reviewed cutout repairs only."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,os,shutil,json
from PIL import Image
import repair_edges as b
import metadata_updates

def plan(kind):
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    if kind=='support':
        source=b.load(b.PACK/'delivery-plan.json');rows=source['records'];dependencies=source['atlas_dependencies']
        accepted=b.load(b.ROOT/'docs/style-repair-20260911/ui-portraits-final-review.json')
        support=b.load(b.PACK/'support-v2.json')['records']
        for r in support:
            assert not r['unresolved_pixels']
            assert b.sha(b.PACK/'support-v2'/r['path'])==r['output_sha256']
        review={'pet_and_item_visual_review':'passed by main agent on full artwork and magnified light/dark edge evidence',
                'portraits_review':'docs/style-repair-20260911/ui-portraits-final-review.json',
                'source_count':6,'atlas_cells_verified':124}
    else:
        source=b.load(b.PACK/'review-v2.json');dependencies=[];rows=[]
        for r in source['records']:
            rows.append({'path':r['path'],'stage':r['output'],'before_sha256':r['source_sha256'],'sha256':r['output_sha256']})
        review={'hero_review':'docs/style-repair-20260911/hero-final-review.json','source_count':32}
        assert (b.ROOT/review['hero_review']).is_file()
    rows=[dict(r) for r in rows]
    for r in rows:
        assert b.sha(b.ROOT/r['path'])==r['before_sha256'],r['path']+' changed; rebase required'
        assert b.sha(b.ROOT/r['stage'])==r['sha256']
    mapping={r['path']:r['sha256'] for r in rows if '/unity-slices/' not in r['path']}
    record={'id':kind+'-'+stamp,'report':f'qdao_cutout_edge_repair_20260910/published-{kind}.json',
            'processing':'Existing artwork only; matte-edge RGB decontamination. Source alpha, dimensions and silhouettes preserved.',**review}
    updates=metadata_updates.make_updates(b.ROOT,mapping,record)
    if kind=='support':
        for prefix in ['', 'qdao_ui_style_recut_v10/staged/']:
            rel=prefix+'designs/attribute-panels/v2-painted/unity-slices/manifest.json';data=b.load(b.ROOT/rel)
            heads={Path(r['path']).stem:r for r in rows if r['path'].startswith(prefix+'designs/attribute-panels/v2-painted/unity-slices/png/')}
            for e in data['sprites']:
                if e['name'] in heads:
                    r=heads[e['name']];e['sha256']=r['sha256'];e['sourceSha256']=r['source_sha256'];e['edge_rgb_repair']=record
            updates[rel]=data
        rel='qdao_ui_style_recut_v10/source-map.attributes.json';data=b.load(b.ROOT/rel)
        heads={r['path'].removeprefix('qdao_ui_style_recut_v10/staged/'):r for r in rows if r['path'].startswith('qdao_ui_style_recut_v10/staged/')}
        for e in data['outputs']:
            if e['path'] in heads:
                r=heads[e['path']];e['outputSha256']=r['sha256'];e['sourceSha256']=r['source_sha256'];e['edge_rgb_repair']=record
        updates[rel]=data
    folder=b.PACK/'metadata-stage'/kind
    for rel,data in updates.items():
        out=folder/rel;b.dump(out,data)
        rows.append({'path':rel,'stage':out.relative_to(b.ROOT).as_posix(),'before_sha256':b.sha(b.ROOT/rel),'sha256':b.sha(out)})
    result={'status':'ready_to_publish','id':record['id'],'kind':kind,'review':review,'records':rows,'dependencies':dependencies,
            'backup_root':f'qdao_cutout_edge_repair_20260910/backups/{record["id"]}','engine_import_performed':False}
    b.dump(b.PACK/f'publish-plan-{kind}.json',result)
    print(json.dumps({'kind':kind,'files':len(rows),'png':sum(r['path'].endswith('.png') for r in rows),'json':len(updates)}))

def publish(kind):
    p=b.load(b.PACK/f'publish-plan-{kind}.json');rows=p['records'];targets={r['path']:r for r in rows}
    for r in rows:
        for key in ['path','stage']:
            assert (b.ROOT/r[key]).resolve().is_relative_to(b.ROOT)
        assert b.sha(b.ROOT/r['path'])==r['before_sha256'],r['path']+' changed since review'
        assert b.sha(b.ROOT/r['stage'])==r['sha256']
    for d in p['dependencies']:
        actual=targets[d['path']]['sha256'] if d['path'] in targets else b.sha(b.ROOT/d['path'])
        assert actual==d['sha256'],'Atlas source changed: '+d['path']
    backup=b.ROOT/p['backup_root'];assert backup.resolve().is_relative_to(b.PACK)
    for r in rows:
        dst=backup/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copy2(b.ROOT/r['path'],dst)
    completed=[]
    try:
        for r in rows:
            dst=b.ROOT/r['path'];assert b.sha(dst)==r['before_sha256'],str(dst)+' changed during publication'
            tmp=dst.with_name(dst.name+'.edge-repair-tmp');assert not tmp.exists()
            shutil.copy2(b.ROOT/r['stage'],tmp);os.replace(tmp,dst);completed.append(r)
        for r in rows:assert b.sha(b.ROOT/r['path'])==r['sha256']
    except Exception:
        # Restore only our own already-written bytes, never a concurrent edit.
        for r in reversed(completed):
            if b.sha(b.ROOT/r['path'])==r['sha256']:shutil.copy2(backup/r['path'],b.ROOT/r['path'])
        raise
    p['status']='published_verified';p['published_utc']=datetime.now(timezone.utc).isoformat();p['verified_files']=len(rows)
    b.dump(b.PACK/f'published-{kind}.json',p)
    print(json.dumps({'status':p['status'],'files':len(rows),'backup':p['backup_root']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['plan','publish']);parser.add_argument('kind',choices=['support','hero']);a=parser.parse_args()
    (plan if a.action=='plan' else publish)(a.kind)
