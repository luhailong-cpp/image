"""Read-only default. --prepare writes audit/proposal/retention TEXT only.

No deletion or canonical metadata mutation is implemented. r10_c13 is excluded.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys
from functools import lru_cache
F=Path(__file__).resolve().parent;T=F.parents[1];ROOT=T.parent;S=ROOT/'r10_c14';OUT=F/'postfinal-audit'
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
IMAGES={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff'}
BINARY=IMAGES|{'.npy','.pyc'}
def norm(p):return str(Path(p).resolve()).casefold()
@lru_cache(maxsize=None)
def ref(p):return dict(file=str(p),sha256=sha(p))
def strings(x,loc='$'):
    if isinstance(x,str):yield loc,x
    elif isinstance(x,dict):
        for k,v in x.items():yield from strings(v,loc+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from strings(v,loc+f'[{i}]')
def refs(x,loc='$'):
    if isinstance(x,dict):
        if isinstance(x.get('file'),str) and isinstance(x.get('sha256'),str):yield loc,x
        for k,v in x.items():yield from refs(v,loc+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from refs(v,loc+f'[{i}]')
def active_record(p):
    parts=[x.casefold() for x in p.parts];name=p.name.casefold()
    if any('history' in x or 'evidence'==x or 'repairs'==x for x in parts):return False
    if any(x in parts for x in ['native','guides']):return False
    if any(s in name for s in ['.generation.','.request.','.call.','retention','audit','proposal','review','assembly']):return False
    return name in ['plan.json','preparation.json','manifest.json','progress.json','index.json','delivery-index.json'] or 'delivery' in name

def build():
    expected={T:'3e8b712967d34934645eb60a94ab57981e944ddcb7557c4dd765546d87be30b2',S:'963d29bf2b73c9ff400d29689a43023135b7653e0cd0159b80f7fc0d6b6f70f3'}
    audit=[];proposals={};checks=[]
    ledger=read(T/'retention-log.json');retired={(norm(v['file']),v['sha256']):v for v in ledger['removed']}
    for v in ledger['removed']:assert v['retiredAfterExport'] is True and not Path(v['file']).exists()
    for tile,digest in expected.items():
        mpath=tile/'output/manifest.json';m=read(mpath);gpath=tile/'output'/f'{tile.name}-candidate.png.generation.json';g=read(gpath)
        assert sha(m['file'])==m['sha256']==g['sha256']==digest and m['scopedLocalSeamsPassed'] is True
        assert m['formalAccepted'] is False and m['clientVerified'] is False and m['navigationVerified'] is False
        # Validate only explicitly current references; acquisition/source reviews
        # may legitimately contain older versions and retain their dated TEXT.
        current=[('currentCandidateGeneration',m['currentCandidateGeneration']),('scopedReviewRecord',m['scopedReviewRecord'])]
        current += [('currentNeighbors.'+k,v) for k,v in m['currentNeighbors'].items()]
        current += [('runtimeDependencies',v) for v in m['runtimeDependencies']]
        current += [('qa',v) for v in m['qa']]
        current += [('pendingMetadataSnapshots',v) for v in m['pendingMetadataSnapshots']]
        for loc,v in current:assert sha(v['file'])==v['sha256'],(loc,v['file'])
        finalreview=read(m['scopedReview']);assert finalreview['candidate']['sha256']==digest
        for q in finalreview['items']:assert sha(q['file'])==q['sha256'] and q['actuallyViewed'] is True and q['nativeScale']==1
        checks.append(dict(tile=tile.name,candidate=dict(file=m['file'],sha256=digest),manifestBefore=ref(mpath),currentRefsVerified=len(current),currentReviewItemsVerified=len(finalreview['items']),currentPixelsAndReviewReferencesComplete=True))
        d=copy.deepcopy(m)
        d['assemblyPlan']=copy.deepcopy(m['plan']);d['assemblyNeighbors']=copy.deepcopy(m['neighbors'])
        d['assemblyPlan']['historicalAcquisitionReference']=True
        for v in d['assemblyNeighbors'].values():v['historicalAcquisitionReference']=True
        d['plan']=ref(tile/'plan.json')
        d['neighbors']=copy.deepcopy(m['currentNeighbors'])
        d['sourceAssemblyRecordsAreHistorical']=True
        d['sourceReferencePolicy']='plan/neighbors/currentNeighbors/runtimeDependencies describe current files. assemblyPlan/assemblyNeighbors/patches describe dated acquisition; immutable sourceManifest and per-image generation TEXT remain unchanged. Lifecycle ledger determines actual retired image availability.'
        if m['plan']['sha256']!=sha(tile/'plan.json'):audit.append(dict(tile=tile.name,issue='manifest.plan copied old assembly plan hash',old=m['plan'],current=ref(tile/'plan.json'),proposedFix='Expose current plan ref and explicitly named historical assemblyPlan.'))
        if m['neighbors']!=m['currentNeighbors']:audit.append(dict(tile=tile.name,issue='manifest.neighbors copied historical source version',proposedFix='Expose current neighbors and explicitly named historical assemblyNeighbors.'))
        if tile==T:
            count=0
            for loc,v in refs(d):
                r=retired.get((norm(v['file']),v['sha256']))
                if r:
                    assert not Path(v['file']).exists()
                    v.update(retiredAfterExport=True,sourceImageAvailable=False,sourceFileLifecycle='historical_pixels_removed_after_final_export',runtimeDependency=False,retentionLog=str(T/'retention-log.json'));count+=1
            d.update(sourceRecordsHistoricalAfterRetention=True,retentionLog=str(T/'retention-log.json'),retentionRecord=ref(T/'retention-log.json'),sourcePolicy='Only files in the completed retention log are actually retired. The115 former processing files remain absent; new repair files are not retired by this audit. All original acquisition TEXT remains unchanged.')
            d['currentAppliedRepair']=dict(application=ref(F/'application.json'),sourceProposalGeneration=ref(F/'r09_c14-proposal.png.generation.json'),sourceAIRecord=ref(F/'repair-native.png.generation.json'),currentCandidateGeneration=ref(gpath))
            audit.append(dict(tile=tile.name,issue='Generic manifest omitted prior retention lifecycle annotations',completedRetirementEntries=len(retired),restoredRetiredReferences=count,proposedFix='Restore accurate current lifecycle annotations from actual completed ledger; never rewrite historical source TEXT.'))
        else:
            d['currentAppliedRepair']=dict(application=ref(S/'repairs/p31-beam-wall/application-v2.json'),sourceAIRecord=ref(S/'repairs/p31-beam-wall/host-result.png.generation.json'),currentCandidateGeneration=ref(gpath))
            d['currentNorthSourceMigration']=ref(F/'application.json')
        proposals[OUT/(tile.name+'-manifest.proposed.json')]=d
    # Keep inventory scoped to r10_c14 and r09_c14's newly created grout repair.
    binaries=sorted([p for scope in [S,F] for p in scope.rglob('*') if p.is_file() and p.suffix.lower() in BINARY and OUT not in p.parents])
    known={norm(p):p for p in binaries};matches={};scanned=0
    # Sibling day records are read-only; no scans/mutations of blocked r10_c13.
    for p in ROOT.parent.rglob('*.json'):
        if T in p.parents or S in p.parents or 'r10_c13' in p.parts or 'tools' in p.parts:continue
        try:doc=read(p)
        except (UnicodeError,json.JSONDecodeError):continue
        scanned+=1;active=active_record(p)
        for loc,value in strings(doc):
            if not ('r10_c14' in value or 'southwest-grout' in value):continue
            if not (':/' in value or ':\\' in value):continue
            try:k=norm(value)
            except (OSError,ValueError):continue
            if k in known:matches.setdefault(k,[]).append(dict(record=ref(p),location=loc,currentConsumer=active,classification='current plan/design/integration declaration' if active else 'historical acquisition/QA/source evidence; not runtime'))
    protected={}
    def keep(p,category,reason):
        p=Path(p);assert p.is_file(),p;protected[norm(p)]=dict(category=category,reason=reason)
    keep(S/'output/r10_c14-candidate.png','game_final','Current native4096 scoped-approved game final.')
    plan=read(S/'plan.json')
    for field in ['nightStructure','proposedSharedStructure']:
        keep(plan[field],'current_design','Current same-frame shared/night geometry design; day task adoption is not claimed.')
    keep(plan['northScopedFreeze']['file'],'current_neighbor_scope','Current north scope explicitly used by current plan after source migration; retain while plan refers to it.')
    for item in read(S/'qa/final-local-review.json')['items']:keep(item['file'],'current_final_QA','Current final scoped review binds these exact original-scale image bytes.')
    # Match the prior reviewed retention convention: keep actual applied mapping
    # fields/selection masks, not unused masks. These are evidence, not runtime.
    for patch in read(S/'output/native-assembly.json')['patches']:
        for kind,v in patch['fields'].items():assert sha(v['file'])==v['sha256'];keep(v['file'],'applied_mapping_evidence','Actual applied '+kind+' field; retained consistent with the previous r09_c14 reviewed retention convention.')
    keep(S/'repairs/west-beam/final-selection-mask.png','applied_selection_evidence','Actual selection mask used by both retained current structure designs.')
    keep(S/'repairs/p31-beam-wall/v2-composite-alpha.png','applied_selection_evidence','Actual local native repair selection alpha referenced by final generation.')
    keep(F/'selection-mask.png','applied_selection_evidence','Actual local native grout repair selection alpha exported into current final.')
    for k,uses in matches.items():
        if any(v['currentConsumer'] for v in uses):keep(known[k],'active_external_reference','Referenced by an external current plan/design/integration declaration; preserve pending owner migration.')
    keepitems=[];remove=[]
    for p in binaries:
        k=norm(p);uses=matches.get(k,[])
        common=dict(**ref(p),bytes=p.stat().st_size,sourceImageAvailable=True,retiredAfterExport=False,externalCurrentReferences=[v for v in uses if v['currentConsumer']],historicalExternalReferenceCount=sum(not v['currentConsumer'] for v in uses))
        if k in protected:keepitems.append(dict(**common,**protected[k]))
        else:
            rel=p.relative_to(S if S in p.parents else F).as_posix()
            reason='Superseded planning/reference/native input or intermediate already exported into accepted final/current design; generation/model/quality/source TEXT is retained.'
            if 'qa-proposed/' in rel:reason='Proposal QA already copied byte-identically into current canonical QA; proposal-view provenance remains TEXT.'
            if p.name in ['r09_c14-proposal.png','v2-proposal-candidate.png']:reason='Whole-image proposal byte-identical to current final; no extra image backup retained after export.'
            if p.suffix.lower()=='.pyc':reason='Regenerable bytecode cache, not artwork or source evidence.'
            gen=Path(str(p)+'.generation.json')
            remove.append(dict(**common,category='retire_after_export_proposal',reason=reason,generationRecord=ref(gen) if gen.exists() else None,plannedLifecycle='Mark retired only after exact-file successful removal and retain original path/hash in ledger.'))
    assert not any(v['externalCurrentReferences'] for v in remove)
    textpaths=sorted([p for scope in [S,F] for p in scope.rglob('*') if p.is_file() and p.suffix.lower() not in BINARY and OUT not in p.parents])
    report=dict(preparedAt=now(),status='read_only_audit_and_exact_retention_proposal',canonicalMetadataModified=False,deletionImplemented=False,deletionExecuted=False,blockedR10c13ScopeExcluded=True,currentMetadataChecks=checks,metadataFindings=audit,metadataProposals=[dict(file=str(p),canonical=str((T if p.name.startswith('r09_') else S)/'output/manifest.json')) for p in proposals],keep=keepitems,remove=remove,preserveAllTextRecords=True,textInventory=[ref(p) for p in textpaths],externalScan=dict(recordsScanned=scanned,matchingReferences=[dict(file=str(known[k]),references=v) for k,v in matches.items()],historicalRequestsAreNotCurrentRuntime=True),unmodifiedExternalScope=dict(r09c14PreviouslyRetainedImages='Outside this new repair scope; no new proposal to remove existing retained p42 or old fields/QA/design.',hostGeneratedImages='Outside workspace scope; not touched.',dayDesigns='Read only; all owned by day task.'),summary=dict(keptBinaryCount=len(keepitems),keptBinaryBytes=sum(v['bytes'] for v in keepitems),proposedRemovalCount=len(remove),proposedRemovalBytes=sum(v['bytes'] for v in remove),preservedTextCount=len(textpaths),currentExternalConflicts=0),executionRules=['Root must inspect this exact path/hash list before authorizing later cleanup.','No deletion executor is provided or run by this script.','Revalidate every normalized absolute target lies in r10_c14 or r09_c14/repairs/southwest-grout and its current SHA matches before later exact-file removal.','Re-audit current external consumers and verify no in-flight image generation or repair needs inputs.','Save mutable current manifest/generation TEXT before lifecycle updates; never modify native request/call/assembly history.','Mark lifecycle retired only for files actually absent after successful removal; never treat a planned deletion as completed.','Current QA, current design, final, integration references and applied selection/mapping evidence remain; all TEXT remains.','Never touch r10_c13 or retry its blocked cleanup.'])
    return report,proposals

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    report,proposals=build()
    if args.prepare:
        for p,d in proposals.items():write(p,d)
        report['metadataProposals']=[dict(file=str(p),sha256=sha(p),canonical=str((T if p.name.startswith('r09_') else S)/'output/manifest.json')) for p in proposals]
        write(OUT/'retention-plan.json',report)
    print(json.dumps(dict(writesTextProposalsOnly=args.prepare,canonicalMetadataModified=False,deletionExecuted=False,summary=report['summary'],findings=report['metadataFindings']),ensure_ascii=False))
