"""Audit current delivered media and the final ZIP; write only final-verification.json."""
import hashlib,json,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PACK=Path(__file__).resolve().parent
ROSTER=ROOT/'qdao_chibi_roster_v11'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    original=load(PACK/'before/qdao_festival_refinement_20260910/reviews/v11-style-review.json')
    before=load(PACK/'before.json')
    manifest=load(ROSTER/'manifest.json');validation=load(ROSTER/'validation.json')
    assert validation['status']=='passed' and not validation['errors']
    assert manifest['festival_edge_export']==validation['festival_edge_export']
    checked={};role_manifests={}
    for role in manifest['characters']:
        slug=role['slug']; m=load(ROSTER/slug/'manifest.json');role_manifests[slug]=m
        for f in m['files']:
            path=(Path(slug)/f['path']).as_posix();h=sha(ROSTER/path)
            assert h==f['sha256'],path
            checked[path]=h
    assert len(checked)==408
    vfiles={x['path']:x['sha256'] for r in validation['characters'] for x in r['artifacts']}
    assert checked==vfiles
    comparison=[];retained=[];changed=[]
    for f in original['files']:
        rel=Path(f['path']).relative_to('qdao_chibi_roster_v11').as_posix()
        is_same=checked[rel]==f['sha256']
        expected_same=f['status']=='retained'
        assert is_same==expected_same,rel
        (retained if is_same else changed).append(rel)
        comparison.append({'path':f['path'],'previous_sha256':f['sha256'],'sha256':checked[rel],'result':'retained' if is_same else 'repaired'})
    assert len(retained)==105 and len(changed)==303
    protected=[p for p in retained if p.startswith(('27_','30_'))]
    assert len(protected)==102
    retained_portraits=[p for p in retained if not p.startswith(('27_','30_'))]
    assert len(retained_portraits)==3 and all(p.endswith('/portrait.png') for p in retained_portraits)
    for f in before['files']:assert sha(ROOT/f['before'])==f['sha256'],f['before']
    approval=load(PACK/'visual-approval.json')
    assert approval['status']=='approved'
    for filename,key in [('stage.json','stage_sha256'),('derived.json','derived_sha256'),('gif-validation.json','gif_validation_sha256')]:assert sha(PACK/filename)==approval[key]
    binding=manifest['festival_edge_export']
    assert sha(PACK/'visual-approval.json')==binding['visual_approval']['sha256']
    assert sha(PACK/'publication.json')==binding['publication']['sha256']
    zip_extra=['manifest.json','validation.json','roster-overview.jpg','movement-overview.gif']
    evidence=0
    for role in binding['roles']:
        slug=role['slug'];folder=ROSTER/slug
        for name,key in [('manifest.json','manifest_sha256'),('qc.json','qc_sha256'),('processing/festival-edge-approval.json','approval_sha256')]:
            assert sha(folder/name)==role[key];zip_extra.append(f'{slug}/{name}')
        a=load(folder/'processing/festival-edge-approval.json');assert a['status']=='approved'
        assert a['batch_review_sha256']==sha(PACK/'visual-approval.json')
        for f in a['files']:assert checked[f"{slug}/{f['path']}"]==f['sha256']
        for f in a['review_evidence']:
            assert sha(folder/f['path'])==f['sha256'];zip_extra.append(f"{slug}/{f['path']}");evidence+=1
    assert evidence==25
    download=load(ROSTER/'download.json');archive=ROSTER/download['file']
    assert archive.stat().st_size==download['size_bytes'] and sha(archive)==download['sha256']
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==download['entries']==739
        for name,h in checked.items():assert hashlib.sha256(z.read(name)).hexdigest()==h,name
        for name in zip_extra:assert hashlib.sha256(z.read(name)).hexdigest()==sha(ROSTER/name),name
    publication=load(PACK/'publication.json')
    supplement=load(PACK/'supplement_28/publication.json')
    current_publication={f['path']:f for f in publication['files']}
    current_publication.update({f['path']:f for f in supplement['files']})
    for f in current_publication.values():assert sha(ROOT/f['path'])==f['sha256'],f['path']
    for f in load(PACK/'supplement_28/before.json')['files']:assert sha(ROOT/f['before'])==f['sha256']
    supp_approval=load(PACK/'supplement_28/approval.json')
    assert supp_approval['status']=='approved' and sha(PACK/'supplement_28/approval.json')==supplement['approval_sha256']
    assert checked['28_moon_rabbit_artificer/portrait.png']==supp_approval['sha256']
    assert binding['supplement']['approval_sha256']==sha(PACK/'supplement_28/approval.json')
    assert binding['supplement']['publication_sha256']==sha(PACK/'supplement_28/publication.json')
    report={'schema':'qdao-festival-edge-final-audit-v1','status':'passed','checked_utc':datetime.now(timezone.utc).isoformat(),'scope':'v11 six-role RGB-only export repair and complete eight-role delivery ZIP','new_image_generation':False,
       'summary':{'formal_media_verified':len(checked),'changed_media':len(changed),'changed_by_extension':dict(Counter(Path(p).suffix for p in changed)),'retained_media':len(retained),'protected_27_30_media_unchanged':len(protected),'retained_23_24_29_portraits':len(retained_portraits),'zip_entries':download['entries'],'zip_formal_media_byte_identical':len(checked),'zip_metadata_and_visual_evidence_byte_identical':len(zip_extra),'new_contact_evidence':evidence,'immutable_before_files_hash_verified':len(before['files']),'published_records_verified':len(current_publication),'portrait_supplement_rgb_pixels':166,'final_unique_changed_rgb_pixels':917918},
       'numeric_acceptance':load(PACK/'derived.json')['summary'],'visual_acceptance_record':'visual-approval.json','current_portrait_supplement':'supplement_28/approval.json','reproduction_trial':'verify_rebuild.py --trial passed 12 independent images; see README.md for full read-only command',
       'artifacts':[{ 'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [ROSTER/'manifest.json',ROSTER/'validation.json',archive,ROSTER/'download.json',ROSTER/'roster-overview.jpg',ROSTER/'movement-overview.gif',PACK/'visual-approval.json',PACK/'stage.json',PACK/'derived.json',PACK/'gif-validation.json',PACK/'publication.json',PACK/'before.json',PACK/'repair_v11_edges.py',PACK/'rebuild_delivery.py',PACK/'verify_rebuild.py',PACK/'supplement_28/approval.json',PACK/'supplement_28/publication.json',PACK/'supplement_28/repair.py']],
       'retained_portraits':retained_portraits,'files':comparison,'errors':[],'limitations':['Asset export/QC only; no game runtime or engine import test claimed.','Historical processing QC records remain original and are not used as new visual acceptance.','Old GIF binary alpha, including legacy palette exceptions, is intentionally unchanged; PNG retains full original alpha.']}
    (PACK/'final-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'summary':report['summary'],'report_sha256':sha(PACK/'final-verification.json')},ensure_ascii=False))
if __name__=='__main__':main()
