import json, hashlib, pathlib, datetime, sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
P = pathlib.Path(__file__).resolve().parent.parent
A = pathlib.Path(__file__).resolve().parent
def read(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ref(p):
    p=pathlib.Path(p)
    return {'path':p.as_posix(), 'sha256':sha(p)}
def verify(p, expected=None, image=False):
    p=pathlib.Path(p)
    out={'path':p.as_posix(), 'exists':p.is_file()}
    if not p.is_file(): return out
    out['sha256']=sha(p)
    out['expectedSha256']=expected
    out['hashMatches']=expected is None or out['sha256']==expected
    if image:
        with Image.open(p) as im:
            out.update(width=im.width, height=im.height, mode=im.mode,
                       alphaExtrema=list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else [255,255])
    return out
def vref(r,image=False):
    return verify(r.get('file',r.get('path')),r.get('sha256'),image)
def assertions_ok(rows):
    return all(r.get('exists') and r.get('hashMatches') for r in rows)
def native_check(s,kind):
    if kind=='day':
        rp=s['generationRecord']; rh=s['generationRecordSha256']; ip=s['file']; ih=s['sha256']; ident=s['cell']
    elif kind=='spring':
        rp=s['generationRecord']['file']; rh=s['generationRecord']['sha256']; ip=s['native']['file'];ih=s['native']['sha256'];ident=s['patchId']
    else:
        rp=s['recordFile'];rh=s['recordSha256'];ip=s['file'];ih=s['sha256'];ident=s['id']
    record=verify(rp,rh); d=read(rp)
    ev=d.get('evidence',{})
    host=d.get('originalToolResultImagePath') or ev.get('sourceOutputPath') or ev.get('toolResultSourcePath') or s.get('toolResultSourcePath')
    source=verify(ip,ih,True)
    source['retiredOriginal']=not source['exists']
    actual=source
    if not source['exists'] and host:
        actual=verify(host,ih,True)
    text_evidence=[]
    for k,v in ev.items():
        if isinstance(v,dict) and (v.get('path') or v.get('file')) and v.get('sha256'):
            text_evidence.append(vref(v))
    passed=(record['exists'] and record['hashMatches'] and d.get('sha256')==ih and
            actual.get('exists') and actual.get('hashMatches') and actual.get('width')==1254 and actual.get('height')==1254 and actual.get('alphaExtrema')==[255,255])
    return {'id':ident,'record':record,'nativeOriginal':source,'verifiedPixelSource':actual,
            'recordSourceHashMatches':d.get('sha256')==ih,'actualModel':d.get('actualModel'),
            'actualQuality':d.get('actualQuality'),'retainedTextEvidence':text_evidence,'passed':passed}

basefile=A/'verified-current-index.json'; baseline=read(basefile)
result={'schemaVersion':1,'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'baseIndex':ref(basefile),'baseCount':45,'scope':'Read-only current-selection, bytes, dimensions, alpha, source and scoped-QA binding audit; no independent full visual acceptance.',
        'baselineFiles':[], 'selectedAdditions':[], 'excluded':[], 'sameCoordinateUpdates':[],
        'formalAccepted':0,'wholeCitiesComplete':0,'indexNotModified':True}
for app in baseline['appearances']:
    for e in app['entries']:
        r=verify(e['path'],e['sha256'],True)
        r.update(appearance=app['appearance'],tileId=e['tileId'])
        result['baselineFiles'].append(r)

for appearance,tile,kind in [('lanxian_day','r09_c09','day'),('lanxian_spring','r09_c11','spring')]:
    root=P/appearance/tile; mf=root/'selected/delivery.manifest.json';m=read(mf)
    select=P/appearance/('progress.json' if kind=='day' else 'current-selection.json'); sd=read(select)
    choices=sd['selectedTiles'] if kind=='day' else sd['currentCandidates']
    choice=next(x for x in choices if x['tile']==tile)
    core=vref(m['outputs']['core'],True); ext=vref(m['outputs']['extended'],True)
    natives=[native_check(s,kind) for s in m['sourceChain']['nativeSources']]
    with Image.open(core['path']) as c,Image.open(ext['path']) as e:
        center_equal=np.array_equal(np.asarray(c.convert('RGB')),np.asarray(e.crop((115,115,4211,4211)).convert('RGB')))
    entry={'appearance':appearance,'tileId':tile,'selectionSource':ref(select),'selectedEntry':choice,
           'manifest':ref(mf),'core':core,'extended':ext,'nativeSources':natives,
           'sourceCount':len(natives),'allNative1254SourcesVerified':all(n['passed'] for n in natives),
           'coreMatchesExtendedCenter':center_equal,'formalAccepted':False,
           'qaStatus':m['status'],'processing':m['processingDeclaration']}
    if kind=='day':
        proof=m['selectionProof'];entry['selectionProof']=vref(proof)
        assembly=read(m['sourceChain']['assembly']['file']);entry['assembly']=vref(m['sourceChain']['assembly'])
        rebuilt=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype=np.uint8)
        byid={n['id']:n for n in natives}
        for mapping in assembly['pixelMappings']:
            with Image.open(byid[mapping['cell']]['verifiedPixelSource']['path']) as src:
                piece=src.convert('RGB').crop(mapping['coreSourceBox']);xy=mapping['coreDestinationXY'];rebuilt.paste(piece,xy)
                coverage[xy[1]:xy[1]+piece.height,xy[0]:xy[0]+piece.width]+=1
        with Image.open(core['path']) as im: entry['independentNativeReconstructionExact']=np.array_equal(np.asarray(rebuilt),np.asarray(im.convert('RGB')))
        entry['independentCoverageEveryPixelOnce']=bool(np.all(coverage==1))
        entry['qaBindings']=[vref(m['qaSummary']['rootFinalReview'])]+[vref(x) for x in m['qaSummary']['teamReports']]
        entry['qaCoverageInherited']=m['qaSummary']['rootCoverage']
        entry['remaining']=m['remaining']
    else:
        entry['assembly']=vref(m['sourceChain']['assembly'])
        entry['qaBindings']=[vref(m['qa']['postreview']),vref(m['qa']['visualReview'])]
        entry['remaining']=m['qa']['remaining'];entry['retention']=m['retention']
    entry['eligibleCompletePixelCandidate']=(core['hashMatches'] and core['width']==4096 and core['height']==4096 and core['alphaExtrema']==[255,255] and center_equal and entry['allNative1254SourcesVerified'] and assertions_ok(entry['qaBindings']) and entry['assembly']['hashMatches'])
    result['selectedAdditions'].append(entry)

appearance='donghai_day';tile='r08_c14';root=P/appearance/tile
select=root/'progress.json';sd=read(select);mf=root/'output/assembly-manifest.json';m=read(mf)
core=vref(m['output'],True); ext=vref(m['extendedContext'],True)
natives=[native_check(s,'fishing') for s in m['nativeSources']]
repair_records=[]
for r in m['postAssemblyRepairChain']:
    rr=read(r['file']); patches=[]
    for patch in rr['patches']:
        px=verify(patch['file'],patch['sha256'],True)
        if not px['exists']: px=verify(patch['evidence']['toolResultSourcePath'],patch['sha256'],True)
        patches.append(px)
    repair_records.append({'record':vref(r),'source':rr['source'],'output':rr['output'],
        'nativePatches':patches,'sourceResampling':rr['sourceResampling'],'upscale':rr['upscale'],
        'outsideRectExactlyUnchanged':rr['outsideRectExactlyUnchanged'],'masks':rr['masks']})
qa=read(sd['waterRepairReview']);qa_binding=verify(sd['waterRepairReview'],m['targetedVisualReview']['sha256'])
qa_images=[vref(x,True) for x in qa['viewedEvidence']]
with Image.open(core['path']) as c,Image.open(ext['path']) as e:
    center_equal=np.array_equal(np.asarray(c.convert('RGB')),np.asarray(e.crop((115,115,4211,4211)).convert('RGB')))
result['selectedAdditions'].append({'appearance':appearance,'tileId':tile,'selectionSource':ref(select),'selectedEntry':sd,'manifest':ref(mf),
    'core':core,'extended':ext,'sourceCount':len(natives),'nativeSources':natives,
    'allNative1254SourcesVerified':all(n['passed'] for n in natives),'coreMatchesExtendedCenter':center_equal,
    'repairChain':repair_records,'qaBinding':qa_binding,'qaImages':qa_images,'qaScope':qa['scope'],'remaining':qa['unreviewedScope'],
    'formalAccepted':False,'eligibleCompletePixelCandidate':bool(sd['completePixelCandidate'] and sd['candidateSha256']==core['sha256'] and core['hashMatches'] and core['alphaExtrema']==[255,255] and core['width']==4096 and core['height']==4096 and center_equal and all(n['passed'] for n in natives) and qa_binding['hashMatches'] and qa['candidate']['sha256']==core['sha256'])})

ts=P/'tianyong_festival/progress.json';t=read(ts)
result['excluded'].append({'appearance':'tianyong_festival','tileId':'r08_c10','reason':'current alpha fragment; incomplete native coverage','source':ref(ts),'coveragePixels':t['coveredNativeTilePixels'],'coverageFraction':t['tileCoverageFraction'],'checkpoint':t['checkpointVersion']})
reg=P/'donghai_lantern/current-candidates.json';d=read(reg)
result['lanternRegistrySnapshot']={'source':ref(reg),'count':len(d['candidates']),'tiles':[x['tile'] for x in d['candidates']]}
if 'r08_c13' not in [x['tile'] for x in d['candidates']]:
    wf=P/'donghai_lantern/r08_c13/west-final/output/west-final-manifest.json';wm=read(wf)
    result['excluded'].append({'appearance':'donghai_lantern','tileId':'r08_c13','reason':'new output exists, but authoritative registry has not selected it and bound manifest marks native visual review pending','outputManifest':ref(wf),'visualReview':wm['visualReview'],'status':wm['status']})
result['otherRegistries']=[ref(P/x) for x in ['penglai_day/tile-manifest.json','penglai_mid_autumn/delivery-index.json','donghai_day/r08_c15/progress.json','lanxian_day/progress.json','lanxian_spring/current-selection.json']]
counts={a['appearance']:len(a['entries']) for a in baseline['appearances']}
for e in result['selectedAdditions']:
    if e['eligibleCompletePixelCandidate']:counts[e['appearance']]+=1
result['proposedCounts']=counts;result['proposedTotal']=sum(counts.values());result['remainingTiles']=1792-result['proposedTotal']
result['baselineAllFilesMatch']=assertions_ok(result['baselineFiles'])
result['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
output=A/'live-refresh-20261008-source-audit.json';output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(output),'sha256':sha(output),'baselineAllFilesMatch':result['baselineAllFilesMatch'],'new':[(x['appearance'],x['tileId'],x['eligibleCompletePixelCandidate'],x['allNative1254SourcesVerified'],x['coreMatchesExtendedCenter']) for x in result['selectedAdditions']], 'proposedCounts':counts,'proposedTotal':result['proposedTotal']},ensure_ascii=False))
