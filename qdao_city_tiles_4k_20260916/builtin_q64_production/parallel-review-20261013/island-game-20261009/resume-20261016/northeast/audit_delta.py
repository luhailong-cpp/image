from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib, json

O = Path(__file__).resolve().parent
R = O.parents[1]
P = R.parents[1] / 'island-game-20261009'
Z = P / 'northeast'
O.mkdir(parents=True, exist_ok=True)
(O / 'snapshots').mkdir(exist_ok=True)

def read(f): return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f, v): Path(f).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()

captured = now()
basefile = R / 'resume-v03/northeast/summary.json'
baseline = read(basefile)
old = {t['tileId']: t for t in baseline['tiles']}
snapshots = []
def snapshot(f):
    f = Path(f); raw = f.read_bytes()
    dst = O / 'snapshots' / f.name
    dst.write_bytes(raw)
    snapshots.append({'file': f.as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'snapshot': dst.as_posix()})
    return json.loads(raw.decode('utf-8-sig'))

selections = {}
for f in sorted(Z.glob('selection-*.json')):
    d = snapshot(f); selections[d['tileId']] = d
coastfile = P / 'accelerated-northeast-coast/current-selection-20261012.json'
coast = snapshot(coastfile)
coast_by = {t['tileId']: t for t in coast['candidates']}
progressfile = Z / 'progress.json'
progress = snapshot(progressfile)
transferred = {f'r{r:02d}_c{c:02d}' for r in (1,2) for c in (10,11,12)}
tiles = []; candidates = []
for tr in range(1,8):
    for tc in range(8,15):
        tid = f'r{tr:02d}_c{tc:02d}'
        if tid in transferred:
            tiles.append({'tileId': tid, 'owner': 'parallel-island-east-residences', 'countIncluded': False,
                          'coreCount': None, 'fullCoverage': None, 'adopted': None,
                          'reason': 'Transferred six coordinates are counted by parallel worker; merge by tileId only.'})
            continue
        a = coast_by.get(tid); sel = selections.get(tid, {})
        matrix = a['selectedCores'] if a else sel.get('cores', [[None]*4 for _ in range(4)])
        n = sum(bool(x) for row in matrix for x in row)
        assert len({(r,c) for r,row in enumerate(matrix) for c,x in enumerate(row) if x}) == n
        f = (a or {}).get('file') or sel.get('candidatePath') or (old.get(tid) or {}).get('file')
        if n < 16: f = None
        t = {'tileId':tid, 'owner':'accelerated-northeast-coast' if a else 'northeast',
             'countIncluded': True, 'coreCount':n, 'missingCoreCount':16-n, 'fullCoverage':n==16,
             'selectedCores':matrix, 'adopted':n==16 and bool(f), 'file':f, 'formalAccepted':False,
             'selectionFile':coastfile.as_posix() if a else (Z/f'selection-{tid}.json').as_posix() if sel else None,
             'pendingIssues':sel.get('pendingIssues',[]), 'productionInternalReview':sel.get('internalReview'),
             'baselineCoreCount':old.get(tid,{}).get('coreCount',0)}
        if f:
            t['sha256'] = sha(f)
            with Image.open(f) as im: t['dimensions'] = list(im.size)
            assert t['dimensions'] == [4096,4096]
            t['candidatePixelsUnchangedFromV03'] = t['sha256'] == old.get(tid,{}).get('sha256')
            if a: assert t['sha256'] == a['sha256']
            review = sel.get('reviewRecord') or sel.get('reviewPath') or sel.get('acceptanceRecord')
            if review and Path(review).exists():
                qr = snapshot(review)
                qhash = qr.get('candidateSha256') or qr.get('sha256')
                t['currentProductionReview'] = {'file':review,'sha256':sha(review),'candidateHashMatches':qhash==t['sha256'],
                    'status':qr.get('status') or qr.get('internalReview'),'internalReview':qr.get('internalReview'),
                    'formalAccepted':qr.get('formalAccepted',False)}
            if tid == 'r05_c11':
                t['internalQA'] = 'requires_native_material_repair_hash_unchanged'
                t['externalQA'] = 'north_lantern_gold_ribs_pending; other known passed segments may be reused individually'
                t['qaEvidence'] = [(R/'resume-v03/northeast-full/summary.json').as_posix()]
            elif tid in ('r02_c13','r02_c14'):
                t['internalQA'] = 'recorded_local_internal_pass_reused_hash_unchanged'
                t['externalQA'] = 'coast_shared_vertical_material_band_unresolved; do not upgrade to full external pass'
                t['qaEvidence'] = [(R/'root-audit-v01/review.md').as_posix()]
            elif t['candidatePixelsUnchangedFromV03']:
                t['internalQA'] = 'prior_internal_evidence_reused_current_candidate_hash_identical'
                t['externalQA'] = 'only previously inspected unchanged edges reused; unavailable neighbors remain pending'
                t['qaEvidence'] = [(R/'resume-v03/northeast-full/r04_c10-late/summary.json').as_posix()] if tid=='r04_c10' else [basefile.as_posix()]
            elif tid in ('r06_c12','r06_c14'):
                t['internalQA'] = 'current_hash_bound_49_item_production_review_reused'
                t['externalQA'] = 'current_top4096_boundary_recorded_passed; left_bottom_missing_neighbors_pending; right_map_edge_for_c14'
                t['qaEvidence'] = [review] if review else []
            else:
                t['internalQA'] = 'changed_candidate_requires_delta_review'
                t['externalQA'] = 'affected_edges_pending'
                t['qaEvidence'] = []
            candidates.append(t)
        else:
            t['internalQA'] = 'partial_with_open_issues' if n else 'no_selected_core_material'
            t['externalQA'] = 'partial_or_unavailable'
        tiles.append(t)

# Only the two partial coordinates generate new audit crops. Complete candidates
# with current hash-bound 49-item records are reused, never redrawn or repackaged.
grid = {}; partial_sources = []; core_cache = {}
old_sourcehash = {r['file']:r['sha256'] for r in baseline.get('partialSourceChecks',[])}
for t in tiles:
    if not t['countIncluded'] or not t['coreCount']: continue
    tid=t['tileId']; tr=int(tid[1:3]);tc=int(tid[5:7])
    if t['fullCoverage']:
        for r in range(4):
            for c in range(4):
                grid[((tr-1)*4+r,(tc-1)*4+c)]={'tileId':tid,'id':tid+f'/{r+1}{c+1}',
                    'file':t['file'],'sha256':t['sha256'],'crop':[c*1024,r*1024,(c+1)*1024,(r+1)*1024], 'new':False}
    else:
        prior=old.get(tid,{}).get('selectedCores',[[None]*4 for _ in range(4)])
        for r,row in enumerate(t['selectedCores']):
            for c,ident in enumerate(row):
                if not ident:continue
                f=Z/'native'/f'{ident}.png'; h=sha(f)
                with Image.open(f) as im: dims=list(im.size)
                assert dims==[1254,1254]
                meta=Path(str(f)+'.generation.json')
                md=read(meta) if meta.exists() else {}
                assert not md.get('sha256') or md['sha256']==h
                new=ident!=prior[r][c] or old_sourcehash.get(f.as_posix())!=h
                e={'tileId':tid,'id':ident,'file':f.as_posix(),'sha256':h,'dimensions':dims,
                   'crop':[115,115,1139,1139],'new':new,'actualModel':md.get('actualModel')}
                grid[((tr-1)*4+r,(tc-1)*4+c)]=e;partial_sources.append(e)

def core(pos):
    if pos not in core_cache:
        e=grid[pos]
        with Image.open(e['file']) as im: core_cache[pos]=im.crop(e['crop']).convert('RGB')
    return core_cache[pos]
edges=[]; crosses=[]
for pos,e in sorted(grid.items()):
    gr,gc=pos
    for nb,axis in [((gr,gc+1),'v'),((gr+1,gc),'h')]:
        if nb not in grid or not(e['new'] or grid[nb]['new']):continue
        a,b=core(pos),core(nb)
        if axis=='v':
            im=Image.new('RGB',(512,1024));im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0))
            wb=[(gc+1)*1024-256,gr*1024,(gc+1)*1024+256,(gr+1)*1024]
        else:
            im=Image.new('RGB',(1024,512));im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256))
            wb=[gc*1024,(gr+1)*1024-256,(gc+1)*1024,(gr+1)*1024+256]
        f=O/f'edge-{gr}-{gc}-{axis}.png';im.save(f);im.close()
        edges.append({'id':f.stem,'file':f.as_posix(),'sha256':sha(f),'axis':axis,'worldBox':wb,
                      'sources':[e,grid[nb]],'status':'pending_visual','resized':False})
    ps=[pos,(gr,gc+1),(gr+1,gc),(gr+1,gc+1)]
    if all(p in grid for p in ps) and any(grid[p]['new'] for p in ps):
        im=Image.new('RGB',(512,512))
        for j,p in enumerate(ps):
            cx=768 if j%2==0 else 0;cy=768 if j<2 else 0
            im.paste(core(p).crop((cx,cy,cx+256,cy+256)),((j%2)*256,(j//2)*256))
        f=O/f'cross-{gr}-{gc}.png';im.save(f);im.close()
        crosses.append({'id':f.stem,'file':f.as_posix(),'sha256':sha(f),'worldPoint':[(gc+1)*1024,(gr+1)*1024],
                        'sources':[grid[p] for p in ps],'status':'pending_visual','resized':False})
boards=[]
for axis in ('v','h'):
    es=[e for e in edges if e['axis']==axis]
    for k in range(0,len(es),4):
        chunk=es[k:k+4];im=Image.new('RGB',(2048,1024),(40,40,40))
        for j,e in enumerate(chunk):
            with Image.open(e['file']) as src:im.paste(src,(j*512,0) if axis=='v' else ((j%2)*1024,(j//2)*512))
        f=O/f'board-{axis}-{k//4+1}.png';im.save(f);im.close()
        boards.append({'file':f.as_posix(),'sha256':sha(f),'edgeIds':[e['id'] for e in chunk],'scale':1,'actuallyViewed':False})
for k in range(0,len(crosses),8):
    chunk=crosses[k:k+8];im=Image.new('RGB',(2048,1024),(40,40,40))
    for j,e in enumerate(chunk):
        with Image.open(e['file']) as src:im.paste(src,((j%4)*512,(j//4)*512))
    f=O/f'board-cross-{k//8+1}.png';im.save(f);im.close()
    boards.append({'file':f.as_posix(),'sha256':sha(f),'crossIds':[e['id'] for e in chunk],'scale':1,'actuallyViewed':False})

def counts(ts):
    return {'tileCount':len(ts),'selectedUniqueCoreCount':sum(t['coreCount'] for t in ts),
        'fullCoverageCount':sum(t['fullCoverage'] for t in ts),'partialCount':sum(0<t['coreCount']<16 for t in ts),
        'emptyCount':sum(t['coreCount']==0 for t in ts),'adopted4096CandidateCount':sum(t['adopted'] for t in ts),
        'formalAcceptedCount':0}
summary={'capturedAtUtc':captured,'status':'frozen_snapshot_delta_crops_pending_visual',
    'scope':'49-coordinate northeast index. Counts include owner39 + coast4 only. Parallel east residences6 are delegated, never counted empty.',
    'counts':counts([t for t in tiles if t['countIncluded']]),
    'ownerCounts':counts([t for t in tiles if t.get('owner')=='northeast']),
    'coastCounts':counts([t for t in tiles if t.get('owner')=='accelerated-northeast-coast']),
    'transferredCoordinates':sorted(transferred),'tiles':tiles,'currentCandidates':(O/'current-candidates.json').as_posix(),
    'baseline':basefile.as_posix(),'selectionSnapshots':snapshots,'partialSourceChecks':partial_sources,
    'newEdges':edges,'newCrosses':crosses,'boards':boards,'productionWrites':0,'generationCalls':0,'gitOperations':0,
    'currentFullCandidateChanges':[t['tileId'] for t in candidates if not t['candidatePixelsUnchangedFromV03']],
    'writeScope':O.as_posix()}
write(O/'current-candidates.json',{'capturedAtUtc':captured,'count':len(candidates),'candidates':candidates})
write(O/'summary.json',summary)
print(json.dumps({'counts':summary['counts'],'ownerCounts':summary['ownerCounts'],'fullChanges':summary['currentFullCandidateChanges'],
    'partialSources':len(partial_sources),'newPartialSources':sum(e['new'] for e in partial_sources),'edges':len(edges),'crosses':len(crosses),
    'boards':[{k:v for k,v in b.items() if k in ('file','edgeIds','crossIds')} for b in boards]},ensure_ascii=False))
