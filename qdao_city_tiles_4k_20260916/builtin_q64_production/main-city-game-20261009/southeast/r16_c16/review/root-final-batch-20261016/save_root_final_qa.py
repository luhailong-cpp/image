from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
R = Path(__file__).resolve().parent
T = R.parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):
    return {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
reuse = read(R/'final-evidence-reuse.json')
selected = read(R/'root-selected-repairs-qa.json')
base_path = T/'review/independent-20261016/visual-qa.json'
base = read(base_path)
nqa = T/'repairs/north-corner-20261016/trial-v1/root-independent-qa-20261016.json'
base_by_name = {e['name']: e for e in base['reviewedCrops']}
changed=[]
for e in reuse['changed']:
    assert ref(Path(e['path']))['sha256'] == e['sha256']
    c={**e}
    c['reviewMethod']='root_actual_native_size_view'
    c['reviewStatus']='local_structure_pass_no_new_gap_or_broken_grout'
    c['observation']='Viewed final combined crop at original resolution; no new local join break.'
    if e['name'] in ('v3072-q1','junction-2048-1024'):
        c['reviewStatus']='structure_pass_finish_pending_M01'
        c['observation']='Stone boundaries remain continuous; existing straight shadow band remains pending.'
    elif e['name'] in ('h2048-q3','junction-3072-2048','p03_04-course-turn'):
        c['reviewStatus']='upper_course_local_pass_lower_course_still_failed'
        c['observation']='Selected upper wrap is continuous; this finding does not pass the separate lower course.'
    elif e['name']=='external-west-q0':
        c['reviewStatus']='W01_local_best_accepted_closure_and_material_watch'
        c['observation']='Short closed coping end improved locally; entire west edge remains failed due to W02 and pending W03/W04.'
    elif e['name']=='external-north-q1':
        c['reviewMethod']='reuse_exact_sha_previously_root_viewed_native_N02'
        c['reviewStatus']='local_structure_pass_after_N02'
        c['observation']='Byte-identical to the already root-viewed final real north join in N02 QA.'
        assert e['sha256']=='524d31cab0d1f8466300f65fd4788fd001e3d3c35b365abe3faf6660394c85be'
        c['sourceQA']=ref(nqa)
    changed.append(c)
reused=[]
for e in reuse['reused']:
    old=e['originalEvidence']
    assert ref(Path(old['path']))['sha256']==old['sha256']
    prior=base_by_name[e['name']]
    assert old['sha256']==prior['sha256']
    reused.append({**e,'reviewStatus':prior['status'],'observation':prior['observation'],
                   'reviewMethod':'reuse_prior_native_QA_pixels_exactly_unchanged'})
assert len(changed)==11 and len(reused)==31
for key in ('candidate','north','west'):
    assert ref(Path(reuse[key]['path']))['sha256']==reuse[key]['sha256']
out={
 'tile':'r16_c16','reviewer':'root',
 'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'candidate':reuse['candidate'],
 'neighbors':{'north':reuse['north'],'west':reuse['west']},
 'sourceQA':{'base':ref(base_path),'selectedRepairs':ref(R/'root-selected-repairs-qa.json'),
             'pixelReuse':ref(R/'final-evidence-reuse.json')},
 'counts':{'totalEvidence':42,'newlyRootViewed':10,'exactShaReusedRootN02':1,'unchangedPriorQAReused':31},
 'scope':'Final selected pixels only; original-resolution native evidence. No global-map or formal acceptance.',
 'changedReviewed':changed,'unchangedReused':reused,
 'internalRasterSeamQA':'continuous_on_reviewed_final_segments',
 'internalArtQA':selected['internalArtQA'],
 'externalNeighborSeamQA':selected['externalNeighborSeamQA'],
 'pending':selected['pending'],
 'formalAccepted':False,
 'actualModel':None,
 'modelEvidence':'Existing built-in image entry returned no actual model identifier.'
}
dest=R/'root-final-evidence-qa-20261016.json'
assert not dest.exists(), 'Preserve existing report; use a new version.'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':ref(dest),'counts':out['counts'],'formalAccepted':False},ensure_ascii=False))

