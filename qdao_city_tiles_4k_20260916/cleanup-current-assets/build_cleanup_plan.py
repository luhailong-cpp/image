"""Build an explicit city-art retention plan; performs no deletion."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib,json,re
from PIL import Image

ROOT=Path(__file__).resolve().parent
ART=ROOT.parent
REPO=ART.parent
SESSION=ART/'builtin_q64_production/resume_single_city_20260921'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
media={'.png','.jpg','.jpeg','.webp','.tif','.tiff','.bmp','.gif','.npy','.npz','.zip'}
keep={}
inputs={}
def load(p):
    data=p.read_bytes();inputs[str(p)]=hashlib.sha256(data).hexdigest()
    return json.loads(data.decode('utf-8-sig'))
def retain(p,reason):
    p=p.resolve()
    if p.is_file() and p.is_relative_to(ART) and p.suffix.lower() in media:
        keep.setdefault(p,set()).add(reason)
def resolve(value,base):
    s=value.replace('\\','/')
    if s.lower().startswith('e:/work/image/'):
        s=str(REPO).replace('\\','/')+'/'+s[len('e:/work/image/'):]
    p=Path(s)
    options=[p] if p.is_absolute() else [base/p,ART/p,REPO/p,SESSION/p]
    return next((q.resolve() for q in options if q.is_file()),None)
def strings(obj):
    if isinstance(obj,str):yield obj
    elif isinstance(obj,dict):
        for v in obj.values():yield from strings(v)
    elif isinstance(obj,list):
        for v in obj:yield from strings(v)
def image_refs(obj,base,reason):
    for s in strings(obj):
        if Path(s).suffix.lower() in media:
            p=resolve(s,base)
            if p:retain(p,reason)

batch=load(ART/'builtin_q64_production/current-batch.json')
state=load(SESSION/'session-state.json')
ledger=load(SESSION/'current-coverage-ledger.json')
catalog=load(ART/'production_catalog.json')
candidates={(x['appearance'],x['tile']):x for x in batch['candidates']}
for t in ledger['tiles']:
    if t['candidateExists']:candidates['tianyong_festival',t['tile']]=t['candidate']
assert len(candidates)==26
qa_roots=set()
for ident,c in candidates.items():
    p=ART/c['file'];assert sha(p)==c['sha256'],str(p)
    with Image.open(p) as im:im.load();assert im.size==(4096,4096)
    retain(p,'latest_selected_4K_candidate:'+':'.join(ident))
    for key in ('qa','review'):
        value=c.get(key)
        if value:
            q=resolve(value['file'] if isinstance(value,dict) else value,ART)
            assert q
            qa_roots.add(q.parent)
            image_refs(load(q),q.parent,'images_explicitly_bound_by_current_visual_review')
for directory in qa_roots:
    for p in directory.rglob('*'):
        retain(p,'current_visual_review_evidence')

selected=[];rejected=set()
for tile in ('r08_c07','r08_c08','r08_c09'):
    d=SESSION/('next_tile_'+tile)
    h=load(d/'handoff-state.json')
    for item in h['selectedPatches']:
        p=Path(item['file']);assert sha(p)==item['sha256']
        retain(p,'selected_native_patch_for_incomplete_tile:'+tile);selected.append(item)
    rejected.update(Path(x['file']).resolve() for x in h['rejectedOrSuperseded'])
    for name in ('guides','references'):
        for p in (d/name).rglob('*'):retain(p,'active_layout_or_material_design:'+tile)
    image_refs(load(d/'layout-record.json'),d,'active_layout_dependencies:'+tile)
    plan=load(d/'plan.json')
    done={x['id'] for x in h['selectedPatches']}
    for item in plan['patches']:
        if item['id'] not in done:
            image_refs(item,d,'pending_patch_input_dependency:'+tile)
    # A selected completed patch can also be the material authority of pending work.
    for item in plan['patches']:
        for s in item.get('submittedImages',[]):
            p=resolve(s,d)
            if p and p not in rejected:retain(p,'current_plan_layout_or_material_reference:'+tile)
for p in rejected:keep.pop(p,None)
assert len(selected)==16
for v in catalog['variants']:
    value=v.get('wholeCityReference',{}).get('file')
    if value:retain(ART/value,'selected_whole_city_design:'+v['city']+'/'+v['variant'])
retain(ART/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png','current_plaza_layout_design')
for p in (ART/'q64_style_reference').rglob('*'):retain(p,'selected_Q_style_design')
for p in (SESSION/'future_geometry_guides/r08_c10').rglob('*'):retain(p,'prepared_next_tile_layout_design')
for name in ('next_tile_r09_c10/references/latest-left-r09_c09-v6/extended-context.png',
             'next_tile_r09_c10/repairs/versions/external-v8/extended-context.png'):
    retain(SESSION/name,'latest_neighbor_context_for_continued_design')

all_media=sorted(p.resolve() for p in ART.rglob('*') if p.is_file() and p.suffix.lower() in media)
for p in all_media:
    assert not p.is_symlink() and p.is_relative_to(ART),str(p)
def item(p):return {'file':str(p),'relativeFile':p.relative_to(ART).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
retained=[];remove=[]
for p in all_media:
    obj=item(p)
    if p in keep:obj['reasons']=sorted(keep[p]);retained.append(obj)
    else:obj['reason']='obsolete_source_version_preview_or_processing_data_not_current_selected_art_or_active_design';remove.append(obj)
result={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'authorization':'User explicitly requested deletion of originals and rollback versions; keep final intended game art and designs.',
        'scopeRoot':str(ART),'deletionScope':'Only explicitly listed city image/processing files. No metadata, source code, client files, other artwork roots, or external generated-image cache.',
        'keep':retained,'delete':remove,'guardInputs':[{'file':p,'sha256':h} for p,h in inputs.items()],
        'summary':{'selectedCandidateCoordinates':26,'selectedTianyongCandidateCoordinates':8,'selectedIncompleteNativePatches':16,
                   'retainedFiles':len(retained),'deleteFiles':len(remove),'retainedBytes':sum(x['bytes'] for x in retained),'deleteBytes':sum(x['bytes'] for x in remove)},
        'formalAcceptedTiles':0,'deliveryReady':False,'historicalSourceHashesRetainedInMetadata':True,
        'rawSourceReplayAfterDeletion':'Unavailable for deleted originals; do not run historical source-byte audits or claim those bytes are retained.'}
with (ROOT/'cleanup-plan.json').open('x',encoding='utf-8') as out:json.dump(result,out,ensure_ascii=False,indent=2)
print(json.dumps(result['summary']))
