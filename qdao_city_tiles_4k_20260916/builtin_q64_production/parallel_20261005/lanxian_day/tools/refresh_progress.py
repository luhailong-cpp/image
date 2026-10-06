"""Refresh task-local status from saved source and selected-delivery records."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json
from workflow import OUTPUT_ROOT,read_json,write_json,sha256

def run(a):
    counts={};selected=[];snapshots={}
    for tile in sorted(OUTPUT_ROOT.glob('r??_c??')):
        records=sorted((tile/'native').glob('r??_c??.png.generation.json'))
        if not records:continue
        items=[]
        for record in records:
            j=read_json(record);p=Path(j['file'])
            if p.exists() and sha256(p)!=j['sha256']:raise ValueError(f'Native changed: {p}')
            cleaned=any((tile/n).exists() for n in ('cleanup-manifest.json','cleanup.manifest.json'))
            if not p.exists() and not cleaned:raise FileNotFoundError(p)
            items.append({'cell':j['cell'],'sha256':j['sha256'],'generationRecord':str(record),
                          'nativePngRetained':p.exists()})
        reused=1 if tile.name=='r08_c09' else 0
        qualified=False;manifest=tile/'selected/delivery.manifest.json'
        if manifest.exists():
            d=read_json(manifest);qualified=d.get('qualifiedComplete4KCandidate') is True
            if qualified:
                for output in d['outputs'].values():
                    if not isinstance(output,dict) or 'file' not in output:continue
                    if sha256(Path(output['file']))!=output['sha256']:raise ValueError('Selected output mismatch')
                selected.append({'tile':tile.name,'manifest':str(manifest),'manifestSha256':sha256(manifest),
                                 'core':d['outputs']['core'],'preview':d['outputs']['preview']})
        counts[tile.name]={'newNativeGenerated':len(items)-reused,'nativeReused':reused,
            'nativeIngestedHistorically':len(items),'nativePngRetained':sum(x['nativePngRetained'] for x in items),
            'qualifiedComplete4KCandidates':int(qualified)};snapshots[tile.name]=items
    handoff=read_json(OUTPUT_ROOT/'handoff.json')
    new_count=sum(v['newNativeGenerated'] for v in counts.values())
    active=counts.get(a.active,{});regional_count=len(list(OUTPUT_ROOT.glob('r??_c??/regional/generation.json')))
    common={'schemaVersion':2,'updatedAtUtc':datetime.now(timezone.utc).isoformat(),
        'targetTiles':256,'targetTilePixels':[4096,4096],'wholeCityPixels':[65536,65536],
        'wholeCityComplete':False,'formalAccepted':0,'clientValidated':False,'runtimePublished':False,
        'readyForProduction':handoff.get('readyForProduction'),'handoffSha256':sha256(OUTPUT_ROOT/'handoff.json'),
        'productionAuthorized':True,'route':'builtin_image_gen','paidApiAllowed':False,
        'newComplete4KCandidates':len(selected),'baselineCandidateCount':len(handoff['baselineCandidates']),
        'nativeDetailPatchesGenerated':new_count,'nativeDetailPatchesReused':sum(v['nativeReused'] for v in counts.values()),
        'nativeDetailPatchesIngestedHistorically':sum(v['nativeIngestedHistorically'] for v in counts.values()),
        'nativeCountScope':'Selected native cell generations only; regional guides, rejected attempts and local AI repair outputs counted separately in their immutable records.',
        'regionalGuidesGenerated':regional_count,'tileSourceCounts':counts,'currentTile':a.active,
        'currentPhase':a.phase,'status':'production_in_progress','currentTileNativeCount':active.get('nativeIngestedHistorically',0),
        'currentTileRequiredNativeCount':16,'currentTileNativeSnapshot':snapshots.get(a.active,[]),
        'selectedTiles':selected,'nextAction':a.next,
        'retention':'Completed tile PNG intermediates retired per each cleanup manifest; final art, technical masks, text provenance and current active reference dependencies retained. Unfinished native sources remain in use.',
        'productionCountPolicy':'Only complete native-pixel4096 composites with recorded inspection count; formal acceptance and client validation remain separate.'}
    if selected:
        last=selected[-1];common.update(lastCompletedTile=last['tile'],candidateTile=last['tile'],
            candidateFile=last['core']['file'],candidateSha256=last['core']['sha256'],preview=last['preview']['file'],
            previewRole='Latest qualified complete candidate overview; preview downsample only',
            selectedDeliveryManifest={'file':last['manifest'],'sha256':last['manifestSha256']})
    for filename in ('progress.json','current-work.json'):
        old=read_json(OUTPUT_ROOT/filename)
        for key in ('appearance','officialModelVerification','sourceAudit','layoutAudit'):
            if key in old:common[key]=old[key]
        destination=OUTPUT_ROOT/filename
        temp=OUTPUT_ROOT/(filename+'.refresh-tmp')
        temp.write_text(json.dumps(common,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temp.replace(destination)
    print(json.dumps({'selectedCandidates':len(selected),'tileSourceCounts':counts,'active':a.active}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--active',required=True);p.add_argument('--phase',required=True);p.add_argument('--next',required=True)
    run(p.parse_args())
