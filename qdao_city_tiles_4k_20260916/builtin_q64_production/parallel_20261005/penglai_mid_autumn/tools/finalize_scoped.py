"""Strict report-based scoped finalization for legacy NW and multi-edge assembly.

Default is read-only validation. No algorithmic check constitutes visual review.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(Path(__file__).resolve().parent/'multi_edge'))
import engine

PASS={'pass','scoped_pass','current_pixels_inspected_neighbor_unverified'}
KEYS={'north':'northCandidate','west':'westCandidate','east':'eastCandidate','south':'southCandidate',
      'northwest':'northWestCandidate','northeast':'northEastCandidate','southwest':'southWestCandidate','southeast':'southEastCandidate'}


def check(value,message):
    if not value:raise ValueError(message)


def now():return datetime.now(timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def key(path):return str(Path(path).resolve()).casefold()
def ref(path):return {'file':str(path),'sha256':sha(path)}
def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def open_image(path):
    with Image.open(path) as image:
        check(image.convert('RGBA').getchannel('A').getextrema()==(255,255),'Image is not opaque: '+str(path))
        return image.convert('RGB')


def context(tile,finalsha):
    check(re.fullmatch(r'r\d{2}_c\d{2}',tile) is not None,'Invalid tile ID')
    r,c=int(tile[1:3]),int(tile[5:7]);check(1<=r<=16 and 1<=c<=16,'Tile outside16x16')
    check(re.fullmatch('[0-9a-f]{64}',finalsha) is not None,'Explicit --finalsha required')
    folder=ROOT/tile;p=folder/'output'/f'{tile}-candidate.png'
    check(sha(p)==finalsha,'Final candidate SHA mismatch')
    candidate=open_image(p);check(candidate.size==(4096,4096),'Candidate must be4096x4096')
    gp=Path(str(p)+'.generation.json');check(read(gp).get('sha256')==finalsha,'Stale candidate generation record')
    choices=[folder/'output/native-assembly.json',folder/'output/multi-edge-assembly.json']
    choices=[q for q in choices if q.is_file()];check(len(choices)==1,'Expected exactly one immutable source assembly')
    mp=choices[0];assembly=read(mp);check(assembly['tile']==tile and assembly.get('sourceCount')==16,'Wrong assembly tile/source count')
    check(key(assembly['file'])==key(p),'Assembly refers to a different candidate path')
    legacy=mp.name=='native-assembly.json';name='NW' if legacy else assembly.get('nativeWorkflow',{}).get('wavefront')
    v,h,corner=engine.orientation(name)
    plan_path=folder/'plan.json';plan=read(plan_path);check(plan['tile']['id']==tile and plan['tile']['finalPixelRect']==[(c-1)*4096,(r-1)*4096,4096,4096],'Plan coordinates mismatch')
    if not legacy:check(plan.get('nativeWorkflow',{}).get('wavefront')==name,'Plan/assembly wavefront mismatch')
    neighbors={};references={'current':ref(p)}
    for role,field in KEYS.items():
        if not plan.get(field):continue
        check(role in [v,h,corner],'Unsupported extra/opposite neighbor in this workflow: '+role)
        path=Path(plan[field]);frozen=plan.get(field+'Sha256')
        check(frozen and sha(path)==frozen,'Missing or changed frozen neighbor: '+role)
        image=open_image(path);check(image.size==(4096,4096),'Neighbor must be4096x4096')
        neighbors[role]=image;references[role]=ref(path)
    depths={p.get('returnDepthInsideCore') for p in assembly.get('patches',[]) if p.get('returnDepthInsideCore') is not None}
    check(len(depths)<=1,'Inconsistent finite return depths')
    depth=next(iter(depths)) if depths else 256
    check(type(depth) is int and 160<=depth<=512,'Invalid return depth')
    return dict(tile=tile,folder=folder,candidate=p,finalsha=finalsha,image=candidate,generation=gp,
                assemblyPath=mp,assembly=assembly,plan=plan,name=name,legacy=legacy,neighbors=neighbors,references=references,returnDepth=depth,
                immutableMetadata=[ref(plan_path),ref(mp),ref(gp)])


def requirements(ctx):
    """Reproduce every required QA pixel in memory from current real sources."""
    folder=ctx['folder'];legacy=ctx['legacy'];out=folder/('qa/native-candidate' if legacy else 'qa/multi-edge-candidate')
    required={}
    for label,image,operation,roles in engine.qa_images(ctx['image'],ctx['neighbors'],ctx['name'],ctx['returnDepth']):
        if legacy:
            label=label.replace('-return-plus','-return-')
            if label.startswith('four-tile-'):
                path=folder/'qa/four-tile-corner.png'
            elif label in ['north-no-neighbor-unverified','west-no-neighbor-unverified']:
                path=folder/'qa'/(label+'.png')
            else:path=out/(label+'.png')
        else:path=out/(label+'.png')
        required[key(path)]=dict(path=path,image=image,operation=operation,roles=roles)
    check(len(required) in [27,28],'Unexpected QA requirement count')
    return required


def extra_image(ctx,path,item):
    """Support common joint-detail sheets or explicit exact crop/paste recipes."""
    match=re.fullmatch(r'(north|east|south|west)-(segment|unrotated)-([1-4])\.png',path.name)
    if match and path.parent.name=='external-details':
        side,kind,index=match.groups();index=int(index)-1;depth=256 if kind=='segment' else 320
        check(side in ctx['neighbors'],'Detail has no real neighbor')
        old,new=ctx['neighbors'][side],ctx['image'];start=index*1024
        if side in ['west','east']:
            result=Image.new('RGB',(depth*2,1024))
            first,second=(old,new) if side=='west' else (new,old)
            result.paste(first.crop((4096-depth,start,4096,start+1024)),(0,0));result.paste(second.crop((0,start,depth,start+1024)),(depth,0))
        else:
            result=Image.new('RGB',(1024,depth*2));first,second=(old,new) if side=='north' else (new,old)
            result.paste(first.crop((start,4096-depth,start+1024,4096)),(0,0));result.paste(second.crop((start,0,start+1024,depth)),(0,depth))
        return result
    recipe=item.get('reproduction')
    check(isinstance(recipe,dict),'Extra QA needs a supported native crop/paste reproduction recipe: '+str(path))
    size=recipe.get('canvasPixels');check(isinstance(size,list) and len(size)==2 and all(type(x)is int and 0<x<=4096 for x in size),'Bad QA canvas')
    result=Image.new('RGB',tuple(size));coverage=Image.new('L',tuple(size),0)
    sources={'current':ctx['image'],**ctx['neighbors']}
    for piece in recipe.get('pieces',[]):
        role=piece['source'];check(role in sources,'Unverified QA source role')
        box=piece['cropLTRB'];xy=piece['pasteXY'];check(len(box)==4 and len(xy)==2 and all(type(x)is int for x in box+xy),'Noninteger QA crop')
        x0,y0,x1,y1=box;check(0<=x0<x1<=4096 and 0<=y0<y1<=4096,'QA crop outside actual source')
        pixels=sources[role].crop(box);transpose=piece.get('transpose')
        check(transpose in [None,'ROTATE_90'],'Unsupported QA resampling')
        if transpose:pixels=pixels.transpose(Image.Transpose.ROTATE_90)
        x,y=xy;w,h=pixels.size;check(0<=x and 0<=y and x+w<=size[0] and y+h<=size[1],'QA paste outside canvas')
        check(coverage.crop((x,y,x+w,y+h)).getextrema()==(0,0),'Overlapping QA pieces')
        result.paste(pixels,(x,y));coverage.paste(255,(x,y,x+w,y+h))
    check(coverage.getextrema()==(255,255),'QA recipe has uncovered pixels')
    return result


def validate_reports(ctx,required):
    folder=ctx['folder'];covered={};reports=[]
    for name,flag in [('horizontal-review.json','scopedPass'),('external-review.json','externalScopedPass'),('root-review.json','scopedPass')]:
        rp=folder/'qa'/name
        try:report_hash=sha(rp);report=read(rp)
        except FileNotFoundError as exc:raise ValueError('Missing review: '+str(rp)) from exc
        review_ref={'file':str(rp),'sha256':report_hash}
        check(report.get(flag) is True,'Review has not passed: '+name)
        check(report.get('issues',[])==[] and report.get('issueCount',0)==0,'Unresolved review issues: '+name)
        candidate=report.get('candidate',{})
        check(candidate.get('sha256')==ctx['finalsha'] and key(candidate.get('file',''))==key(ctx['candidate']),'Stale or wrong candidate review: '+name)
        items=[]
        for field in ['items','mainQA','supplementalQA']:
            values=report.get(field,[]);check(isinstance(values,list),'Invalid visual review list: '+name+'/'+field);items.extend(values)
        check(bool(items),'Empty visual review: '+name)
        seen=set()
        for item in items:
            p=Path(item['file']);k=key(p)
            check(p.resolve().is_relative_to(folder.resolve()),'Review image outside tile')
            check(k not in seen,'Duplicate QA item in report: '+str(p));seen.add(k)
            check(item.get('actuallyViewed') is True and type(item.get('nativeScale')) in [int,float] and item['nativeScale']==1,'No actual native-scale visual review: '+str(p))
            check(item.get('verdict') in PASS,'Non-passing image verdict: '+str(p))
            if item['verdict']=='current_pixels_inspected_neighbor_unverified':
                check(k in required and required[k]['operation'].get('noNeighbor') is True,'Neighbor-unverified verdict is only valid for an absent-neighbor boundary')
            check(sha(p)==item.get('sha256'),'QA image SHA changed after visual review: '+str(p))
            expected=required[k]['image'] if k in required else extra_image(ctx,p,item)
            actual=open_image(p)
            check(actual.size==expected.size and actual.tobytes()==expected.tobytes(),'QA image does not reproduce current candidate/neighbor pixels: '+str(p))
            accepted=copy.deepcopy(item);accepted.update(sourceReview=review_ref,sourceReviewCandidateSha256=ctx['finalsha'],verifiedAgainstCurrentCandidatePixels=True)
            if k in covered:check(covered[k]['sha256']==accepted['sha256'],'Conflicting duplicate image reviews')
            covered[k]=accepted
        check(sha(rp)==report_hash,'Review changed while its items were checked: '+name);reports.append(review_ref)
    missing=set(required)-set(covered)
    check(not missing,'Required QA missing from passed reports: '+', '.join(sorted(missing)))
    return covered,reports


def frozen(ctx):
    check(sha(ctx['candidate'])==ctx['finalsha'],'Candidate changed during validation')
    for role,record in ctx['references'].items():
        check(sha(record['file'])==record['sha256'],'Source changed during validation: '+role)
    for record in ctx.get('immutableMetadata',[]):
        check(sha(record['file'])==record['sha256'],'Source metadata changed during validation: '+str(record['file']))


def frozen_reviews(covered,reports):
    for record in list(covered.values())+reports:
        check(sha(record['file'])==record['sha256'],'Review input changed during validation: '+str(record['file']))


def prepare_corner(ctx,required):
    corners=[value for value in required.values() if value['path'].name.startswith('four-tile-')]
    check(len(corners)==1,'Three true neighboring tiles are required for a four-tile corner')
    item=corners[0];path=item['path'];gp=Path(str(path)+'.generation.json')
    check(not path.exists() and not gp.exists(),'Refuse to overwrite existing corner QA')
    frozen(ctx);path.parent.mkdir(parents=True,exist_ok=True);item['image'].save(path)
    write(gp,dict(**ref(path),createdAt=now(),pixels=list(item['image'].size),nativeScale=1,actuallyViewed=False,verdict='pending_visual_QA',operation=item['operation'],sources=[ctx['references'][role] for role in item['roles']],formalAccepted=False))
    return dict(corner=ref(path),acceptanceWritten=False,actuallyViewed=False)


def pending_snapshot(path):
    if not path.exists():return None
    existing=read(path);check(existing.get('scopedLocalSeamsPassed') is not True,'Refuse to overwrite scoped-pass metadata: '+str(path))
    digest=sha(path);snapshot=path.parent/'evidence'/(path.stem+'-pending-'+digest+'.json')
    if snapshot.exists():check(sha(snapshot)==digest,'Pending snapshot path collision')
    else:
        snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(path.read_bytes())
    return ref(snapshot)


def source_metadata(ctx, previous):
    """Current source pointers plus explicit immutable acquisition/lifecycle history."""
    folder=ctx['folder'];assembly=ctx['assembly']
    current={k:copy.deepcopy(v) for k,v in ctx['references'].items() if k!='current'}
    result=dict(plan=ref(folder/'plan.json'),neighbors=current,currentNeighbors=copy.deepcopy(current),
                assemblyPlan=copy.deepcopy(assembly['plan']),assemblyNeighbors=copy.deepcopy(assembly.get('neighbors',{})),
                patches=copy.deepcopy(assembly.get('patches',[])),sourceAssemblyRecordsAreHistorical=True,
                sourceReferencePolicy='plan/neighbors/currentNeighbors are current; assemblyPlan/assemblyNeighbors/patches preserve dated acquisition. Actual retired availability is declared only by the verified completed retention ledger.')
    result['assemblyPlan']['historicalAcquisitionReference']=True
    for value in result['assemblyNeighbors'].values():value['historicalAcquisitionReference']=True
    def references(value):
        if isinstance(value,dict):
            if isinstance(value.get('file'),str) and isinstance(value.get('sha256'),str):yield value
            for child in value.values():yield from references(child)
        elif isinstance(value,list):
            for child in value:yield from references(child)
    # Preserve concrete current applied-repair/source records, never arbitrary
    # old acceptance flags or unvalidated prior image pointers.
    for field in ['currentAppliedRepair','currentNorthSourceMigration']:
        if field in previous:
            value=copy.deepcopy(previous[field])
            for record in references(value):check(sha(record['file'])==record['sha256'],'Stale retained current source record: '+record['file'])
            result[field]=value
    ledger_ref=previous.get('retentionLog')
    if ledger_ref is None:return result
    ledger_path=Path(ledger_ref['file'] if isinstance(ledger_ref,dict) else ledger_ref)
    check(ledger_path.resolve().is_relative_to(folder.resolve()),'Retention ledger outside tile')
    ledger_hash=sha(ledger_path);ledger=read(ledger_path)
    declared=previous.get('retentionRecord',ledger_ref if isinstance(ledger_ref,dict) else None)
    if declared:check(declared.get('sha256')==ledger_hash,'Stale retention ledger hash')
    retired={}
    for record in ledger.get('removed',[]):
        if record.get('retiredAfterExport') is not True:continue
        check(record.get('sourceImageAvailable') is False,'Contradictory completed retirement entry')
        path=Path(record['file']);check(path.resolve().is_relative_to(folder.resolve()),'Retired source outside tile')
        check(not path.exists(),'Retired source unexpectedly available: '+str(path))
        retired[(key(path),record['sha256'])]=record
    for record in references(result):
        if (key(record['file']),record['sha256']) in retired:
            record.update(retiredAfterExport=True,sourceImageAvailable=False,sourceFileLifecycle='historical_pixels_removed_after_final_export',runtimeDependency=False,retentionLog=str(ledger_path))
    check(sha(ledger_path)==ledger_hash,'Retention ledger changed during validation')
    result.update(sourceRecordsHistoricalAfterRetention=True,retentionLog=str(ledger_path),retentionRecord={'file':str(ledger_path),'sha256':ledger_hash},
                  sourcePolicy=previous.get('sourcePolicy','Only actually completed retirement entries are unavailable; all acquisition TEXT remains immutable.'))
    return result


def approve(ctx,required,covered,reports):
    folder=ctx['folder'];mp=folder/'output/manifest.json';review_path=folder/'qa/final-local-review.json';progress_path=folder/'progress.json'
    # Check all protected records before writing even a text snapshot.
    for p in [mp,review_path,progress_path]:
        if p.exists():check(read(p).get('scopedLocalSeamsPassed') is not True,'Refuse to overwrite scoped-pass metadata: '+str(p))
    source_overrides=source_metadata(ctx,read(mp) if mp.exists() else {})
    frozen(ctx);frozen_reviews(covered,reports);snapshots=[record for record in [pending_snapshot(mp),pending_snapshot(review_path),pending_snapshot(progress_path)] if record]
    sides=['north','east','south','west'];verified={s:s in ctx['neighbors'] for s in sides};missing=[s for s in sides if not verified[s]]
    r,c=int(ctx['tile'][1:3]),int(ctx['tile'][5:7]);outer=[s for s,(dr,dc) in engine.ROLES.items() if s in sides and not(1<=r+dr<=16 and 1<=c+dc<=16)]
    interior_missing=[s for s in missing if s not in outer]
    timestamp=now();review=dict(reviewedAt=timestamp,candidate=ref(ctx['candidate']),sourceReviews=reports,items=list(covered.values()),requiredQACount=len(required),allRequiredQAImagesActuallyViewed=True,scopedLocalSeamsPassed=True,issueCount=0,issues=[],externalSeamsVerified=verified,missingExternalNeighbors=missing,missingInteriorNeighbors=interior_missing,intentionalWorldBoundarySides=outer,formalAccepted=False,navigationVerified=False,clientVerified=False,pendingMetadataSnapshots=snapshots,acceptanceNote='Visual reports accept this tile internal seams and supplied actual-neighbor edges only. Unprovided interior neighbors remain pending; coverage is not whole-city, navigation or client acceptance.')
    write(review_path,review)
    manifest=copy.deepcopy(ctx['assembly']);manifest.update(file=str(ctx['candidate']),sha256=ctx['finalsha'],status='native_4K_candidate_available_scoped_neighbor_QA_passed',scopedLocalSeamsPassed=True,acceptedAtScoped=timestamp,sourceManifest=ref(ctx['assemblyPath']),assemblyCandidateSha256=ctx['assembly']['sha256'],currentCandidateGeneration=ref(ctx['generation']),currentNeighbors={k:v for k,v in ctx['references'].items() if k!='current'},qa=[covered[k] for k in required],scopedReview=str(review_path),scopedReviewRecord=ref(review_path),runtimeDependencies=[ref(ctx['candidate'])],externalSeamsVerified=verified,missingExternalNeighbors=missing,missingInteriorNeighbors=interior_missing,intentionalWorldBoundarySides=outer,pendingMetadataSnapshots=snapshots,formalAccepted=False,navigationVerified=False,clientVerified=False,acceptanceNote=review['acceptanceNote'])
    manifest.update(source_overrides)
    write(mp,manifest)
    write(progress_path,dict(updatedAt=timestamp,tile=ctx['tile'],nativePatches=16,pixels=[4096,4096],completePixelCoverage=True,file=str(ctx['candidate']),sha256=ctx['finalsha'],scopedLocalSeamsPassed=True,externalSeamsVerified=verified,missingExternalNeighbors=missing,missingInteriorNeighbors=interior_missing,intentionalWorldBoundarySides=outer,formalAccepted=False,navigationVerified=False,clientVerified=False))
    return dict(scopedAcceptanceWritten=True,manifest=ref(mp),candidateSha256=ctx['finalsha'],requiredQACount=len(required))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tile',required=True);p.add_argument('--finalsha',required=True)
    action=p.add_mutually_exclusive_group();action.add_argument('--approve',action='store_true');action.add_argument('--prepare-corner',action='store_true')
    args=p.parse_args();ctx=context(args.tile,args.finalsha);required=requirements(ctx)
    if args.prepare_corner:result=prepare_corner(ctx,required)
    else:
        covered,reports=validate_reports(ctx,required);frozen(ctx);frozen_reviews(covered,reports)
        result=approve(ctx,required,covered,reports) if args.approve else dict(validationPassed=True,writesPerformed=False,candidateSha256=args.finalsha,requiredQACount=len(required))
    print(json.dumps(result))


if __name__=='__main__':main()
