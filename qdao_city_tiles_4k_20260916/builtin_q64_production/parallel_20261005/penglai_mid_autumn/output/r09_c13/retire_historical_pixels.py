"""Plan scoped c13 retention and update text evidence after PowerShell deletion.

This script never deletes files. Delete only via delete_retired_pixels.ps1.
"""
from pathlib import Path
import hashlib, json, sys, shutil
from datetime import datetime, timezone

B = Path(__file__).resolve().parents[2]
O = B / 'output/r09_c13'
Q = B / 'qa/west-final'
H = B / 'repairs/west/closure3'
LOG = O / 'retention-log.json'
EXPECTED = '9de5b3325de9ba147072aab2b5e7effbbd10a033894b928711e572b895429e4d'
DIRS = ['rows','native','guides','assembly','assembly-registered','repairs/west','qa','references','output/r09_c13']
EXTS = {'.png','.jpg','.jpeg','.webp','.npy','.npz'}
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p): return {'file':str(p),'sha256':sha(p)}
def key(p): return str(Path(p).resolve()).lower()
def allowed(p):
    p=Path(p).resolve()
    return any(p.is_relative_to((B/d).resolve()) for d in DIRS) and not any(x.startswith('r10_') for x in p.relative_to(B).parts)

assert sha(O/'r09_c13.png') == EXPECTED
m = read(O/'manifest.json')
assert sha(m['westSource']) == m['westSourceSha256']

if len(sys.argv)==1 or sys.argv[1]=='plan':
    assert not LOG.exists(), 'Retention plan already exists; inspect rather than overwrite.'
    retained={}
    def keep(p,role):
        p=Path(p).resolve();assert p.exists() and allowed(p)
        retained[key(p)]={'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'role':role}
    keep(O/'r09_c13.png','sole runtime production 4K tile')
    keep(B/'references/r09_c13-structure.png','current shared structure design')
    for p in (B/'assembly-registered').iterdir():
        if p.name.endswith(('.mask.png','.flow.npy','.colorCorrection.npy')):keep(p,'actual internal registration field')
    for p in O.iterdir():
        if p.name.endswith(('.mask.png','.flow.npy','.colorCorrection.npy')) or p.name=='closure-combined-mask.png':keep(p,'actual west registration or combined mask')
    for name in ['anchored-mask.png','anchored-flow.npy','anchored-tone.npy']:
        keep(B/'repairs/west/diagnostic'/name,'applied roof endpoint registration field')
    for label in ['upper','lower']:
        for suffix in ['mask.png','flow.npy','colorCorrection.npy']:keep(H/f'{label}.{suffix}','applied AI closure registration field')
    for name in ['mask.png','color-field.npy','row-color-estimates.npy']:
        keep(Q/'color-trial'/name,'applied bounded color correction field and estimation evidence')
    review=read(Q/'review.json')
    for item in review['qa']+review['finalMicroQA']:
        assert item['actuallyViewed'] and sha(item['file'])==item['sha256']
        keep(item['file'],'current passed final native QA')
    for p in (B/'qa/registered').glob('*.png'):keep(p,'passed internal baseline QA; final west crossings supersede affected left band')
    trial=read(H/'merge-trial-record.json')
    for item in trial['qa']:
        assert item['actuallyViewed'] and sha(item['file'])==item['sha256']
        keep(item['file'],'passed applied native repair return QA')
    # Mixed-tile preview may be used by ROOT/r10 work; preserve without modification.
    if (B/'qa/three-tile-corner.png').exists():keep(B/'qa/three-tile-corner.png','protected cross-task preview; unchanged')
    delete=[]
    for directory in DIRS:
        for p in (B/directory).rglob('*'):
            if not p.is_file() or p.suffix.lower() not in EXTS:continue
            assert allowed(p),p
            if key(p) not in retained:
                delete.append({'path':str(p.resolve()),'relativePath':str(p.relative_to(B)),'sha256':sha(p),
                               'bytes':p.stat().st_size,'kind':'retired_image' if p.suffix.lower()!='.npy' else 'unused_diagnostic_field',
                               'reason':'Superseded native source, layout, assembly, rejected/unused diagnostic, or superseded QA; final 4K and current scoped QA retained.'})
    text_evidence=[]
    for directory in DIRS:
        for p in (B/directory).rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.json','.txt','.md','.py','.ps1'}:
                text_evidence.append({'path':str(p.resolve()),'sha256BeforeRetirement':sha(p)})
    d={'tile':'r09_c13','createdAt':now(),'status':'planned_not_deleted','root':str(B),
       'allowedDirectories':[str((B/d).resolve()) for d in DIRS],
       'final':ref(O/'r09_c13.png'),'oldWestSource':{'file':m['westSource'],'sha256':m['westSourceSha256']},
       'excluded': ['r10_c12','r10_c13','ROOT progress/current-work/current-preview','all paths outside ROOT','global and other-task sources'],
       'policy':'User 2026-09-23 retention rule and ROOT explicit c13 cleanup delegation. Preserve all prompt/config/model/source/hash text and actually applied fields. Future context comes from final 4K.',
       'runtimeDependencies':[ref(O/'r09_c13.png')],'retained':list(retained.values()),'deleted':delete,
       'textEvidenceBeforeRetirement':text_evidence,'deletedCount':0}
    write(LOG,d)
    print(json.dumps({'plannedDeleteCount':len(delete),'retainedBinaryCount':len(retained),'plannedBytes':sum(x['bytes'] for x in delete),'log':str(LOG)}))
    sys.exit()

assert sys.argv[1]=='finalize'
log=read(LOG)
assert log['status']=='deleted_pending_text_retirement'
deleted={key(v['path']):v for v in log['deleted']}
for v in log['deleted']:assert allowed(v['path']) and not Path(v['path']).exists()
for v in log['retained']:assert sha(v['path'])==v['sha256']
at=now()
policy={'retiredAt':at,'historicalPixelsRetired':True,'historicalSourceImagesAreRuntimeDependencies':False,
        'runtimeDependencies':[ref(O/'r09_c13.png')], 'retentionLog':str(LOG),
        'futureNeighborContext':'Crop the finalized 4096x4096 output. Retired paths and hashes are provenance only, not available image inputs.',
        'sourceRecordInterpretation':'Original generation parameters, model nulls, tool paths and hashes remain historical evidence. Tool output paths outside ROOT were not touched and are not runtime dependencies.'}
archives=[]
def archive(p):
    rel=p.relative_to(B)
    target=O/'evidence/pre-retention-text'/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists()
    shutil.copyfile(p,target)
    archives.append({'original':str(p),'archive':str(target),'sha256':sha(target)})
def annotate(d):
    if isinstance(d,list):
        for v in d:annotate(v)
    elif isinstance(d,dict):
        retired=[]
        for k,v in list(d.items()):
            if isinstance(v,str) and (v.startswith('D:') or v.startswith('d:')):
                rec=deleted.get(key(v))
                if rec:retired.append({'field':k,'path':v,'sha256':rec['sha256'],'available':False,'runtimeDependency':False})
            elif isinstance(v,(dict,list)):annotate(v)
        if retired:
            d['retiredPixelReferences']=retired
            if 'file' in [v['field'] for v in retired]:
                d['imageRetained']=False;d['pixelArtifactAvailability']='retired_after_4K_export'
            if 'source' in [v['field'] for v in retired]:d['sourceImageRetained']=False
            if 'sourceRetained' in d:d['sourceRetained']=False

# Mark retired source generation records; keep exact prior texts with their hashes.
source_records=[]
for directory in DIRS:
    for p in (B/directory).rglob('*.png.generation.json'):
        if 'evidence' in p.relative_to(B).parts:continue
        d=read(p)
        if key(d.get('file','')) in deleted:source_records.append(p)
for p in source_records:
    archive(p);d=read(p);annotate(d);d['retention']=policy;d['sourceRetained']=False;write(p,d)

# Current operation records must explicitly distinguish retired art from retained fields.
records=[B/'repairs/west/diagnostic/anchored-record.json',Q/'color-trial/trial-record.json',H/'merge-trial-record.json']
for p in records:
    archive(p);d=read(p);annotate(d);d['retention']=policy;write(p,d)

def refresh_current_text_refs(d):
    if isinstance(d,list):
        for v in d:refresh_current_text_refs(v)
    elif isinstance(d,dict):
        p=d.get('file')
        if p and Path(p) in records and 'sha256' in d:d['sha256']=sha(p)
        for v in d.values():
            if isinstance(v,(dict,list)):refresh_current_text_refs(v)

for p in [Q/'review.json',O/'manifest.json',O/'r09_c13.png.generation.json']:
    archive(p);d=read(p);annotate(d);refresh_current_text_refs(d);d['retention']=policy
    if p.name=='manifest.json':d['westFinalQA']=ref(Q/'review.json')
    if p.name=='r09_c13.png.generation.json':d['qa']=ref(Q/'review.json')
    write(p,d)

log.update(status='complete',completedAt=at,textRecordArchives=archives,
           historicalPixelsRetired=True,finalSha256Reverified=sha(O/'r09_c13.png'),
           runtimeDependencies=[ref(O/'r09_c13.png')],currentManifest=ref(O/'manifest.json'),
           currentGeneration=ref(O/'r09_c13.png.generation.json'),currentQA=ref(Q/'review.json'))
write(LOG,log)
assert sha(O/'r09_c13.png')==EXPECTED
assert sha(m['westSource'])==m['westSourceSha256']
print(json.dumps({'status':'complete','deleted':len(deleted),'retainedBinaryCount':len(log['retained']),
                  'retiredSourceGenerationRecords':len(source_records),'textArchives':len(archives),'finalSHA':EXPECTED,
                  'logSHA':sha(LOG)},ensure_ascii=False))
